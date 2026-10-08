"""Refresh vocabulary data without requests, request hooks, or database use."""

import fcntl
import hashlib
import json
import os
import subprocess
import sys
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

from flask import current_app
from flask_caching.backends import FileSystemCache, RedisCache

from histarchexplorer import cache
from histarchexplorer.api.api_access import ApiAccess
from histarchexplorer.services.cache_jobs import (
    MAX_ATTEMPTS as MAX_RETRY_ATTEMPTS, retry_transient, set_api_headers)

CATEGORIES = ('standard', 'place', 'custom', 'value', 'tools', 'system')
LEASE_SECONDS = 180
HEARTBEAT_SECONDS = 15
MAX_ATTEMPTS = MAX_RETRY_ATTEMPTS
ACTIVE_STATES = ('queued', 'running')
ROOT = Path(__file__).resolve().parents[2]


class LeaseLost(RuntimeError):
    """The worker no longer owns the refresh and must stop writing."""


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _empty_status() -> dict:
    return {
        'state': 'idle', 'total': 0, 'successful': 0, 'failed': 0,
        'started_at': '', 'updated_at': '', 'finished_at': ''}


class _Coordinator:
    """Durable status and locks independent of cache.clear().

    A host flock is inherited by the worker for its entire lifetime. Redis
    installations additionally use a token-owned, renewable distributed lease
    in a separate database: even an unprefixed cache FLUSHDB cannot erase it.
    The coordination database must not be used for cached application data.
    """

    def __init__(self, app):
        self.directory = Path(app.config.get(
            'VOCABULARY_REFRESH_DIR',
            Path(app.instance_path) / 'vocabulary-refresh'))
        self.directory.mkdir(parents=True, exist_ok=True)
        backend = cache.cache
        if isinstance(backend, _OwnedCache):
            backend = backend.backend
        self.redis = None
        if isinstance(backend, RedisCache):
            from redis import Redis
            options = dict(backend._write_client.connection_pool
                           .connection_kwargs)
            cache_db = int(options.get('db', 0))
            options['db'] = int(app.config.get(
                'VOCABULARY_REFRESH_REDIS_DB', cache_db + 1))
            if options['db'] == cache_db:
                raise ValueError('Refresh coordination needs a separate DB')
            self.cache_db = cache_db
            self.redis_db = options['db']
            options['socket_timeout'] = 5
            options['socket_connect_timeout'] = 5
            self.redis = Redis(**options)
            prefix = backend.key_prefix or ''
            identity = hashlib.sha256(str(prefix).encode()).hexdigest()[:16]
            self.key = f'histarchexplorer:vocabulary-refresh:{identity}'
        elif not isinstance(backend, FileSystemCache):
            raise RuntimeError('Vocabulary refresh needs a shared cache')

    def host_lock(self):
        """Acquire a lifetime lock, never unlinking the locked inode."""
        fd = os.open(self.directory / 'worker.lock', os.O_CREAT | os.O_RDWR,
                     0o600)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            os.close(fd)
            return None
        return fd

    def _file_update(self, update):
        """Serialize read/compare/write and atomically replace status files."""
        with (self.directory / 'status.lock').open('a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            path = self.directory / 'status.json'
            value = json.loads(path.read_text()) if path.exists() else {}
            result, new_value = update(value)
            if new_value is not None:
                temporary = path.with_suffix(f'.{uuid.uuid4().hex}.tmp')
                try:
                    temporary.write_text(json.dumps(new_value))
                    os.replace(temporary, path)
                finally:
                    temporary.unlink(missing_ok=True)
            return result

    def read(self):
        if self.redis:
            value = self.redis.get(self.key + ':status')
            return json.loads(value) if value else {}
        return self._file_update(lambda value: (value, None))

    def acquire(self, token, status):
        """Queue atomically; expired previous jobs can be replaced."""
        record = dict(status, token=token, expires=time.time() + LEASE_SECONDS)
        if self.redis:
            return bool(self.redis.eval(
                "if redis.call('exists', KEYS[1]) == 1 then return 0 end "
                "redis.call('set', KEYS[1], ARGV[1], 'EX', ARGV[2]); "
                "redis.call('set', KEYS[2], ARGV[3]); return 1",
                2, self.key + ':lease', self.key + ':status', token,
                LEASE_SECONDS, json.dumps(record)))

        # The caller holds the lifetime flock: a previous local owner died.
        return self._file_update(lambda value: (True, record))

    def owns(self, token):
        if self.redis:
            value = self.redis.get(self.key + ':lease')
            return value == token.encode()
        value = self.read()
        return (value.get('token') == token
                and value.get('expires', 0) > time.time())

    def write(self, token, status, finish=False):
        """Renew/release only our lease, never modifying a replacement job."""
        record = dict(status, token=token, expires=time.time() + LEASE_SECONDS)
        if self.redis:
            operation = (
                "redis.call('del', KEYS[1]); " if finish else
                "redis.call('expire', KEYS[1], ARGV[2]); ")
            return bool(self.redis.eval(
                "if redis.call('get', KEYS[1]) ~= ARGV[1] "
                "then return 0 end " + operation +
                "redis.call('set', KEYS[2], ARGV[3]); return 1",
                2, self.key + ':lease', self.key + ':status', token,
                LEASE_SECONDS, json.dumps(record)))

        def update(value):
            if value.get('token') != token:
                return False, None
            return True, record

        return self._file_update(update)

    def interrupt(self, record):
        """Mark a dead/expired owner without clobbering concurrent starts."""
        token = record.get('token')
        status = dict(record, state='interrupted', updated_at=_timestamp(),
                      finished_at=_timestamp())
        if self.redis:
            self.redis.eval(
                "if redis.call('exists', KEYS[1]) == 1 then return 0 end "
                "local s = redis.call('get', KEYS[2]); "
                "if not s or cjson.decode(s).token ~= ARGV[1] "
                "then return 0 end "
                "redis.call('set', KEYS[2], ARGV[2]); return 1",
                2, self.key + ':lease', self.key + ':status', token,
                json.dumps(status))
        else:
            self._file_update(lambda value: (
                True, status if value.get('token') == token else None))


class _OwnedCache:
    """Fence memoized writes, including responses from a stalled old worker.

    Redis atomically checks ownership in the coordination database and writes
    in the data database. This also handles suspension beyond lease expiry:
    no old response or namespace reset can overwrite a replacement refresh.
    File cache writes use the same token guard under the durable status lock.
    """

    def __init__(self, backend, coordinator, token):
        self.backend = backend
        self.coordinator = coordinator
        self.token = token

    def __getattr__(self, name):
        return getattr(self.backend, name)

    def set(self, key, value, timeout=None):
        coordinator = self.coordinator
        if coordinator.redis:
            ttl = self.backend._normalize_timeout(timeout)
            result = self.backend._write_client.eval(
                "redis.call('select', ARGV[1]); "
                "local owner = redis.call('get', ARGV[2]); "
                "redis.call('select', ARGV[3]); "
                "if owner ~= ARGV[4] then return 0 end "
                "if tonumber(ARGV[7]) == -1 then "
                "redis.call('set', ARGV[5], ARGV[6]); else "
                "redis.call('set', ARGV[5], ARGV[6], 'EX', ARGV[7]); end; "
                "return 1", 0, coordinator.redis_db,
                coordinator.key + ':lease', coordinator.cache_db,
                self.token, self.backend._get_prefix() + key,
                self.backend.serializer.dumps(value), ttl)
        else:
            def update(record):
                if record.get('token') != self.token:
                    return False, None
                return self.backend.set(key, value, timeout), None

            result = coordinator._file_update(update)
        if not result:
            raise LeaseLost('Vocabulary refresh cache write rejected')
        return result

    def set_many(self, mapping, timeout=None):
        return [key for key, value in mapping.items()
                if self.set(key, value, timeout)]


def get_vocabulary_cache_status() -> dict:
    """Return public progress, detecting dead workers without request hooks."""
    coordinator = _Coordinator(current_app._get_current_object())
    record = coordinator.read()
    if record.get('state') in ACTIVE_STATES:
        if coordinator.redis:
            dead = not coordinator.owns(record['token'])
        else:
            fd = coordinator.host_lock()
            dead = fd is not None
            if fd is not None:
                try:
                    coordinator.interrupt(record)
                finally:
                    os.close(fd)
        if coordinator.redis and dead:
            coordinator.interrupt(record)
        record = coordinator.read()
    return {key: record.get(key, value)
            for key, value in _empty_status().items()}


def start_vocabulary_refresh() -> bool:
    """Launch a detached worker; False means a refresh already owns the lock.

    Startup errors release only this job's lease and are propagated to the
    caller. Credentials come from application configuration, never arguments.
    """
    coordinator = _Coordinator(current_app._get_current_object())
    fd = coordinator.host_lock()
    if fd is None:
        return False
    token = uuid.uuid4().hex
    now = _timestamp()
    status = dict(_empty_status(), state='queued', started_at=now,
                  updated_at=now)
    acquired = False
    try:
        acquired = coordinator.acquire(token, status)
        if not acquired:
            return False
        subprocess.Popen(
            [sys.executable, str(ROOT / 'warm_vocabulary_cache.py'),
             '--job-token', token, '--lock-fd', str(fd)],
            cwd=str(ROOT), pass_fds=(fd,), start_new_session=True,
            stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL)
        return True
    except Exception:
        if acquired:
            status.update(state='failed', updated_at=_timestamp(),
                          finished_at=_timestamp())
            coordinator.write(token, status, finish=True)
        raise
    finally:
        os.close(fd)


def collect_vocabulary_ids(tree: dict) -> list[int]:
    """Iteratively collect unique positive IDs from all six category trees."""
    ids = set()
    pending = [node for category in CATEGORIES
               for node in tree.get(category, [])]
    seen = set()
    while pending:
        node = pending.pop()
        if not isinstance(node, dict) or id(node) in seen:
            continue
        seen.add(id(node))
        id_ = node.get('id')
        if type(id_) is int and id_ > 0:
            ids.add(id_)
        children = node.get('children', [])
        if isinstance(children, list):
            pending.extend(children)
    return sorted(ids)


_retry = retry_transient


def _api_context(app):
    set_api_headers()


def run_vocabulary_refresh(token: str, lock_fd: int) -> dict:
    """Warm memoized data directly, with two contexts and a renewable lease.

    The inherited flock is held until every detail task has stopped. Lost
    Redis ownership terminates the process immediately, including in-flight
    threads, before the old worker can continue writing after lease expiry.
    """
    app = current_app._get_current_object()
    coordinator = _Coordinator(app)
    status = coordinator.read()
    mutex = threading.Lock()
    stop = threading.Event()

    def publish(finish=False):
        status['updated_at'] = _timestamp()
        if not coordinator.write(token, status, finish):
            raise LeaseLost('Vocabulary refresh lease lost')

    def heartbeat():
        with app.app_context():
            while not stop.wait(HEARTBEAT_SECONDS):
                try:
                    with mutex:
                        publish()
                except Exception:
                    # Fail closed while there is still ample lease time.
                    return os._exit(1)

    def detail(id_):
        with app.app_context():
            _api_context(app)
            if not coordinator.owns(token):
                raise LeaseLost('Vocabulary refresh lease lost')
            _retry(lambda: ApiAccess.get_vocabulary_detail(id_))
            if not coordinator.owns(token):
                raise LeaseLost('Vocabulary refresh lease lost')

    thread = None
    backend = cache.cache
    try:
        if status.get('token') != token or not coordinator.owns(token):
            raise LeaseLost('Vocabulary refresh lease lost')
        app.extensions['cache'][cache] = _OwnedCache(
            backend, coordinator, token)
        status['state'] = 'running'
        publish()
        thread = threading.Thread(target=heartbeat, daemon=True)
        thread.start()
        _api_context(app)
        cache.delete_memoized(ApiAccess.get_vocabulary_tree)
        cache.delete_memoized(ApiAccess.get_vocabulary_detail)
        tree = _retry(ApiAccess.get_vocabulary_tree)
        if not coordinator.owns(token):
            raise LeaseLost('Vocabulary refresh lease lost')
        ids = collect_vocabulary_ids(tree)
        with mutex:
            status['total'] = len(ids)
            publish()
        with ThreadPoolExecutor(max_workers=2) as executor:
            tasks = [executor.submit(detail, id_) for id_ in ids]
            for task in as_completed(tasks):
                try:
                    task.result()
                    key = 'successful'
                except LeaseLost:
                    raise
                except Exception:
                    key = 'failed'
                with mutex:
                    status[key] += 1
                    publish()
        status['state'] = 'partial' if status['failed'] else 'completed'
    except LeaseLost:
        raise
    except Exception:
        app.logger.exception('Vocabulary refresh failed')
        status['state'] = 'failed'
    finally:
        stop.set()
        if thread is not None:
            thread.join()
        try:
            if status.get('token') == token:
                status['finished_at'] = _timestamp()
                publish(finish=True)
        finally:
            app.extensions['cache'][cache] = backend
            os.close(lock_fd)
    return {key: status[key] for key in _empty_status()}
