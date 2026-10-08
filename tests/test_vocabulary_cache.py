"""Worker tests avoid database setup, real subprocesses, and external APIs."""

import os
import struct
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import MagicMock, patch

import pytest
import requests
from flask import g, has_app_context
from flask_caching.backends import FileSystemCache, RedisCache

from histarchexplorer import app, cache
from histarchexplorer.api.api_access import ApiAccess
from histarchexplorer.services import vocabulary_cache as worker


@pytest.fixture(scope='session', autouse=True)
def setup_database():
    """These application-context-only tests deliberately need no database."""
    yield


@pytest.fixture()
def isolated_worker(tmp_path, monkeypatch):
    backend = FileSystemCache(str(tmp_path / 'cache'), default_timeout=1234)
    monkeypatch.setitem(app.extensions['cache'], cache, backend)
    monkeypatch.setitem(app.config, 'VOCABULARY_REFRESH_DIR',
                        str(tmp_path / 'coordination'))
    monkeypatch.setitem(app.config, 'API_TOKEN', 'test-secret')
    with app.app_context(), patch('histarchexplorer.connect') as connect:
        yield backend
        connect.assert_not_called()


@pytest.fixture()
def queued_worker(isolated_worker):
    descriptors = []

    def inherit(*args, **kwargs):
        descriptors.append(os.dup(kwargs['pass_fds'][0]))
        return MagicMock()

    with patch.object(worker.subprocess, 'Popen',
                      side_effect=inherit) as popen:
        assert worker.start_vocabulary_refresh()
        coordinator = worker._Coordinator(app)
        token = coordinator.read()['token']
        yield token, descriptors, popen
    for fd in descriptors:
        try:
            os.close(fd)
        except OSError:
            pass


def execute(queued):
    token, descriptors, _ = queued
    return worker.run_vocabulary_refresh(token, descriptors.pop())


def http_error(status):
    response = requests.Response()
    response.status_code = status
    return requests.HTTPError('Upstream error', response=response)


def test_collect_all_categories_iteratively():
    tree = {category: [{'id': index + 1}]
            for index, category in enumerate(worker.CATEGORIES)}
    node = {'id': 7, 'children': []}
    tree['standard'].extend([
        node, {'id': True}, {'id': -1}, {'id': '8'}, {'id': 0}, None])
    for index in range(8, 2008):
        child = {'id': index, 'children': []}
        node['children'].append(child)
        node = child
    node['children'].append(tree['standard'][0])
    tree['system'].append({'id': 7})
    tree['ignored'] = [{'id': 9999}]
    assert worker.collect_vocabulary_ids(tree) == list(range(1, 2008))


def test_start_is_nonblocking_and_duplicate_is_rejected(queued_worker):
    _, _, popen = queued_worker
    status = worker.get_vocabulary_cache_status()
    assert status['state'] == 'queued'
    assert status['started_at'] and status['updated_at']
    assert status['finished_at'] == ''
    assert not worker.start_vocabulary_refresh()
    popen.assert_called_once()
    args, kwargs = popen.call_args
    assert args[0][0] == sys.executable
    assert os.path.isabs(args[0][1])
    assert kwargs['cwd'] == str(worker.ROOT)
    assert kwargs['start_new_session']
    assert 'test-secret' not in repr(popen.call_args)
    popen.return_value.__enter__.assert_not_called()
    popen.return_value.wait.assert_not_called()


def test_global_clear_keeps_job_and_lock(queued_worker):
    cache.set('vocabulary-test', {'old': True})
    cache.clear()
    assert cache.get('vocabulary-test') is None
    assert worker.get_vocabulary_cache_status()['state'] == 'queued'
    assert not worker.start_vocabulary_refresh()
    queued_worker[2].assert_called_once()


def test_simultaneous_starts_launch_only_one_process(isolated_worker):
    descriptors = []
    rendezvous = threading.Barrier(2)

    def inherit(*args, **kwargs):
        descriptors.append(os.dup(kwargs['pass_fds'][0]))
        return MagicMock()

    def start():
        with app.app_context():
            rendezvous.wait(timeout=2)
            return worker.start_vocabulary_refresh()

    try:
        with patch.object(worker.subprocess, 'Popen',
                          side_effect=inherit) as popen, \
                ThreadPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(start) for _ in range(2)]
            assert sorted(future.result() for future in futures) == [
                False, True]
        popen.assert_called_once()
        assert worker.get_vocabulary_cache_status()['state'] == 'queued'
    finally:
        for fd in descriptors:
            os.close(fd)


def test_start_failure_releases_lock_and_records_failure(isolated_worker):
    with patch.object(worker.subprocess, 'Popen',
                      side_effect=OSError('Cannot start')):
        with pytest.raises(OSError, match='Cannot start'):
            worker.start_vocabulary_refresh()
    status = worker.get_vocabulary_cache_status()
    assert status['state'] == 'failed'
    assert status['finished_at']
    coordinator = worker._Coordinator(app)
    fd = coordinator.host_lock()
    assert fd is not None
    os.close(fd)


def test_dead_process_is_interrupted_and_can_restart(queued_worker):
    _, descriptors, popen = queued_worker
    os.close(descriptors.pop())
    assert worker.get_vocabulary_cache_status()['state'] == 'interrupted'
    assert worker.get_vocabulary_cache_status()['finished_at']
    assert worker.start_vocabulary_refresh()
    assert popen.call_count == 2


def test_idle_status(isolated_worker):
    assert worker.get_vocabulary_cache_status() == worker._empty_status()


@pytest.mark.parametrize('failure', [
    requests.ConnectionError(), requests.Timeout(), http_error(429),
    http_error(500), http_error(503)])
def test_transient_errors_retry_with_bounded_backoff(failure):
    operation = MagicMock(side_effect=[failure, failure, {'ok': True}])
    with patch.object(worker.time, 'sleep') as sleep:
        assert worker._retry(operation) == {'ok': True}
    assert operation.call_count == 3
    assert [call.args[0] for call in sleep.call_args_list] == [1, 2]


@pytest.mark.parametrize('failure', [
    http_error(404), http_error(401), ValueError('Invalid payload')])
def test_permanent_errors_do_not_retry(failure):
    operation = MagicMock(side_effect=failure)
    with patch.object(worker.time, 'sleep') as sleep:
        with pytest.raises(type(failure)):
            worker._retry(operation)
    operation.assert_called_once()
    sleep.assert_not_called()


def test_retry_exhaustion():
    operation = MagicMock(side_effect=requests.Timeout())
    with patch.object(worker.time, 'sleep'):
        with pytest.raises(requests.Timeout):
            worker._retry(operation)
    assert operation.call_count == worker.MAX_ATTEMPTS


def test_worker_contexts_invalidation_and_shared_ttl(queued_worker):
    cache.set('unrelated', 'kept')
    with patch.object(ApiAccess, '_get_vocabulary',
                      return_value={'old': True}):
        ApiAccess.get_vocabulary_tree()
        ApiAccess.get_vocabulary_detail(1)
        ApiAccess.get_vocabulary_detail(999)
    headers = []

    def fetch(endpoint):
        assert has_app_context()
        assert not hasattr(g, 'db')
        headers.append(dict(g.api_headers))
        if endpoint == 'tree':
            return {'standard': [{'id': 1}], 'system': [{'id': 2}]}
        return {'id': int(endpoint)}

    backend = cache.cache
    with patch.object(ApiAccess, '_get_vocabulary', side_effect=fetch), \
            patch.object(cache, 'delete_memoized',
                         wraps=cache.delete_memoized) as invalidate, \
            patch.object(backend, 'set', wraps=backend.set) as store:
        result = execute(queued_worker)
        assert ApiAccess.get_vocabulary_detail(1) == {'id': 1}
        assert ApiAccess.get_vocabulary_detail(999) == {'id': 999}
    assert result['state'] == 'completed'
    assert (result['total'], result['successful'], result['failed']) == (
        2, 2, 0)
    assert result['started_at'] <= result['updated_at']
    assert result['finished_at']
    assert worker.get_vocabulary_cache_status() == result
    assert invalidate.call_args_list[0].args == (
        ApiAccess.get_vocabulary_tree,)
    assert invalidate.call_args_list[1].args == (
        ApiAccess.get_vocabulary_detail,)
    assert headers == [{'Authorization': 'Bearer test-secret'}] * 4
    assert cache.get('unrelated') == 'kept'
    key = next(call.args[0] for call in store.call_args_list
               if call.args[1] == {'id': 999})
    with open(backend._get_filename(key), 'rb') as cached_file:
        expires = struct.unpack('I', cached_file.read(4))[0]
    assert 1232 <= expires - time.time() <= 1234


def test_partial_detail_failure_continues(queued_worker):
    def fetch(id_):
        if id_ == 2:
            raise http_error(404)
        return {'id': id_}

    with patch.object(ApiAccess, 'get_vocabulary_tree', return_value={
            'custom': [{'id': 1}, {'id': 2}, {'id': 3}]}), \
            patch.object(ApiAccess, 'get_vocabulary_detail',
                         side_effect=fetch) as detail, \
            patch.object(cache, 'delete_memoized'):
        result = execute(queued_worker)
    assert result['state'] == 'partial'
    assert (result['total'], result['successful'], result['failed']) == (
        3, 2, 1)
    assert detail.call_count == 3


def test_tree_failure_fails_job_without_details(queued_worker):
    with patch.object(ApiAccess, 'get_vocabulary_tree',
                      side_effect=http_error(503)) as tree, \
            patch.object(ApiAccess, 'get_vocabulary_detail') as detail, \
            patch.object(cache, 'delete_memoized'), \
            patch.object(worker.time, 'sleep'):
        result = execute(queued_worker)
    assert result['state'] == 'failed'
    assert result['total'] == result['successful'] == result['failed'] == 0
    assert result['finished_at']
    assert tree.call_count == 3
    detail.assert_not_called()
    assert worker.get_vocabulary_cache_status() == result


def test_maximum_two_detail_threads_and_separate_contexts(queued_worker):
    mutex = threading.Lock()
    rendezvous = threading.Barrier(2)
    active = 0
    maximum = 0
    contexts = []

    def fetch(id_):
        nonlocal active, maximum
        with mutex:
            active += 1
            maximum = max(maximum, active)
            contexts.append(g._get_current_object())
        rendezvous.wait(timeout=2)
        time.sleep(0.005)
        with mutex:
            active -= 1
        assert g.api_headers == {'Authorization': 'Bearer test-secret'}
        return {'id': id_}

    with patch.object(ApiAccess, 'get_vocabulary_tree', return_value={
            'tools': [{'id': index} for index in range(1, 7)]}), \
            patch.object(ApiAccess, 'get_vocabulary_detail',
                         side_effect=fetch), \
            patch.object(cache, 'delete_memoized'):
        result = execute(queued_worker)
    assert result['state'] == 'completed'
    assert maximum == 2
    assert len({id(context) for context in contexts}) == 6


def test_no_token_config_uses_empty_headers(queued_worker, monkeypatch):
    monkeypatch.setitem(app.config, 'API_TOKEN', '')

    def tree():
        assert g.api_headers == {}
        return {}

    with patch.object(ApiAccess, 'get_vocabulary_tree', side_effect=tree), \
            patch.object(cache, 'delete_memoized'):
        assert execute(queued_worker)['state'] == 'completed'


def test_heartbeat_renews_during_long_tree_fetch(queued_worker, monkeypatch):
    monkeypatch.setattr(worker, 'HEARTBEAT_SECONDS', 0.005)
    renewed = threading.Event()
    original = worker._Coordinator.write
    writes = []

    def write(self, token, status, finish=False):
        writes.append(threading.current_thread().name)
        if threading.current_thread() is not threading.main_thread():
            renewed.set()
        return original(self, token, status, finish)

    def tree():
        assert renewed.wait(timeout=2)
        assert not worker.start_vocabulary_refresh()
        return {}

    with patch.object(worker._Coordinator, 'write', write), \
            patch.object(ApiAccess, 'get_vocabulary_tree', side_effect=tree), \
            patch.object(cache, 'delete_memoized'):
        assert execute(queued_worker)['state'] == 'completed'
    assert len(writes) >= 4


def test_old_owner_cannot_overwrite_or_release_replacement(queued_worker):
    old, _, _ = queued_worker
    coordinator = worker._Coordinator(app)
    replacement = dict(coordinator.read(), token='replacement', state='queued')
    coordinator._file_update(lambda value: (True, replacement))
    assert not coordinator.write(old, {'state': 'completed'}, finish=True)
    assert not coordinator.write(old, {'state': 'running'})
    assert coordinator.read() == replacement
    with pytest.raises(worker.LeaseLost):
        execute(queued_worker)
    assert coordinator.read() == replacement


def test_stale_owner_cannot_write_cached_data(queued_worker):
    old, _, _ = queued_worker
    coordinator = worker._Coordinator(app)
    owned_cache = worker._OwnedCache(cache.cache, coordinator, old)
    assert owned_cache.set('detail', {'id': 1})
    replacement = dict(coordinator.read(), token='replacement')
    coordinator._file_update(lambda value: (True, replacement))
    with pytest.raises(worker.LeaseLost):
        owned_cache.set('detail', {'id': 2})
    with pytest.raises(worker.LeaseLost):
        owned_cache.set_many({'namespace': 'old'})
    assert cache.get('detail') == {'id': 1}
    assert cache.get('namespace') is None


def test_heartbeat_failure_terminates_worker(queued_worker, monkeypatch):
    monkeypatch.setattr(worker, 'HEARTBEAT_SECONDS', 0.005)
    terminated = threading.Event()
    original = worker._Coordinator.write

    def write(self, token, status, finish=False):
        if threading.current_thread() is not threading.main_thread():
            raise ConnectionError('Coordination unavailable')
        return original(self, token, status, finish)

    def tree():
        assert terminated.wait(timeout=2)
        return {}

    with patch.object(worker._Coordinator, 'write', write), \
            patch.object(ApiAccess, 'get_vocabulary_tree', side_effect=tree), \
            patch.object(cache, 'delete_memoized'), \
            patch.object(worker.os, '_exit',
                         side_effect=lambda code: terminated.set()) as exit_:
        execute(queued_worker)
    exit_.assert_called_once_with(1)


def test_redis_data_writes_are_atomically_fenced(isolated_worker):
    backend_client = MagicMock()
    backend_client.eval.return_value = 1
    backend = RedisCache(host=backend_client, default_timeout=1234,
                         key_prefix='test:')
    coordinator = MagicMock(redis_db=5, cache_db=4, key='coordination')
    coordinator.redis = True
    owned_cache = worker._OwnedCache(backend, coordinator, 'owner')
    assert owned_cache.set('detail', {'id': 1})
    args = backend_client.eval.call_args.args
    assert "'select'" in args[0] and 'owner ~= ARGV[4]' in args[0]
    assert args[1:7] == (0, 5, 'coordination:lease', 4, 'owner', 'test:detail')
    assert args[-1] == 1234
    assert backend.serializer.loads(args[-2]) == {'id': 1}
    backend_client.eval.return_value = 0
    with pytest.raises(worker.LeaseLost):
        owned_cache.set('detail', {'id': 2})
    backend_client.set.assert_not_called()


def test_redis_uses_separate_db_and_owner_checked_operations(
        isolated_worker, monkeypatch):
    cache_client = MagicMock()
    cache_client.connection_pool.connection_kwargs = {
        'host': 'localhost', 'port': 6379, 'db': 4}
    backend = RedisCache(host=cache_client, key_prefix='test:')
    monkeypatch.setitem(app.extensions['cache'], cache, backend)
    redis_client = MagicMock()
    redis_client.eval.return_value = 1
    redis_client.get.return_value = b'owner'
    with patch('redis.Redis', return_value=redis_client) as redis:
        coordinator = worker._Coordinator(app)
    assert redis.call_args.kwargs['db'] == 5
    assert redis.call_args.kwargs['socket_timeout'] == 5
    assert coordinator.acquire('owner', worker._empty_status())
    assert coordinator.owns('owner')
    assert not coordinator.owns('other')
    assert coordinator.write('owner', {'state': 'running'})
    assert coordinator.write('owner', {'state': 'completed'}, finish=True)
    scripts = [call.args[0] for call in redis_client.eval.call_args_list]
    assert "'exists'" in scripts[0] and "'EX'" in scripts[0]
    assert "~= ARGV[1]" in scripts[1] and "'expire'" in scripts[1]
    assert "~= ARGV[1]" in scripts[2] and "'del'" in scripts[2]
    backend.clear()
    cache_client.keys.assert_called_once_with('test:*')
    redis_client.delete.assert_not_called()
    monkeypatch.setitem(app.config, 'VOCABULARY_REFRESH_REDIS_DB', 4)
    with pytest.raises(ValueError, match='separate DB'):
        worker._Coordinator(app)


def test_redis_rejected_lease_closes_host_lock(isolated_worker, monkeypatch):
    coordinator = worker._Coordinator(app)
    with patch.object(worker._Coordinator, 'acquire', return_value=False), \
            patch.object(worker.subprocess, 'Popen') as popen:
        assert not worker.start_vocabulary_refresh()
    popen.assert_not_called()
    fd = coordinator.host_lock()
    assert fd is not None
    os.close(fd)


def test_redis_missing_lease_marks_interrupted(isolated_worker, monkeypatch):
    coordinator = MagicMock()
    coordinator.redis = True
    record = dict(worker._empty_status(), state='running', token='dead')
    finished = dict(record, state='interrupted')
    coordinator.read.side_effect = [record, finished]
    coordinator.owns.return_value = False
    with patch.object(worker, '_Coordinator', return_value=coordinator):
        assert worker.get_vocabulary_cache_status()['state'] == 'interrupted'
    coordinator.interrupt.assert_called_once_with(record)


def test_cli_direct_run_and_duplicate(isolated_worker, monkeypatch):
    import warm_vocabulary_cache as cli

    monkeypatch.setattr(sys, 'argv', ['warm_vocabulary_cache.py'])
    with patch.object(ApiAccess, 'get_vocabulary_tree', return_value={}), \
            patch.object(cache, 'delete_memoized'):
        assert cli.main() == 0
    assert worker.get_vocabulary_cache_status()['state'] == 'completed'
    coordinator = worker._Coordinator(app)
    fd = coordinator.host_lock()
    try:
        with patch.object(cli, 'run_vocabulary_refresh') as run:
            assert cli.main() == 0
        run.assert_not_called()
    finally:
        os.close(fd)
