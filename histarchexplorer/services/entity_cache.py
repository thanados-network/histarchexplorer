"""Entity cache: age tracking, background warm-up and dashboard statistics.

Every API fetch of an entity stores a timestamp next to the memoized
``PresentationView``. The timestamp allows refreshing entities after
``ENTITY_CACHE_MAX_AGE_DAYS`` on access or in a background job, and it
feeds the age statistics of the admin dashboard.
"""

import json
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Optional

import requests
from flask import current_app, g

from histarchexplorer import cache
from histarchexplorer.services.cache_jobs import (
    JobTracker, retry_transient, set_api_headers, timestamp)

MODES = ('warm', 'stale', 'refresh')
MAX_WORKERS = 2
MAX_ERRORS = 20
STATS_KEY = 'cache_dashboard_stats'
STATS_SECONDS = 120
SECONDS_PER_DAY = 86400
AGE_BUCKETS = (('day', 1), ('three_days', 3), ('week', 7))
JOB_DEFAULTS = {
    'state': 'idle', 'mode': '', 'total': 0, 'processed': 0, 'fetched': 0,
    'skipped': 0, 'failed': 0, 'errors': [], 'started_at': '',
    'updated_at': '', 'finished_at': ''}


def _stamp_key(entity_id: int) -> str:
    return f'entity_cached_at:{entity_id}'


def max_age_seconds() -> float:
    return float(current_app.config.get(
        'ENTITY_CACHE_MAX_AGE_DAYS', 7)) * SECONDS_PER_DAY


def cached_at(entity_id: int) -> Optional[float]:
    return cache.get(_stamp_key(entity_id))


def record_entity_cached(entity_id: int) -> None:
    """Remember when the entity was last fetched from the API."""
    cache.set(_stamp_key(entity_id), time.time())
    try:
        with open(_seen_path(), 'a') as seen:
            seen.write(f'{entity_id}\n')
    except OSError:
        current_app.logger.warning('Entity registry not writable')


def _seen_path() -> Path:
    return entity_job().directory / 'entity-seen.txt'


def is_stale(stamp: Optional[float]) -> bool:
    return stamp is not None and time.time() - stamp > max_age_seconds()


def forget_entity(entity_id: int) -> None:
    """Remove the cached entity together with its timestamp."""
    from histarchexplorer.api.presentation_view import PresentationView
    cache.delete_memoized(
        PresentationView.from_api, PresentationView, entity_id)
    cache.delete(_stamp_key(entity_id))


def ensure_entity_fresh(entity_id: int) -> None:
    """Drop an entity older than the maximum age so it is fetched anew.

    Entries cached before age tracking existed have no timestamp; the
    warm-up job adopts them instead of refetching.
    """
    if is_stale(cached_at(entity_id)):
        forget_entity(entity_id)


def list_entity_ids(case_study_ids: list[int]) -> list[int]:
    """Return IDs of all entities of the given case studies."""
    from histarchexplorer.api.api_access import PROXIES

    def fetch() -> list[dict[str, Any]]:
        response = requests.get(
            f"{current_app.config['API_URL']}system_class/all",
            params={
                'type_id': case_study_ids, 'limit': 0, 'show': ['none'],
                'format': 'lpx'},
            headers=g.api_headers,
            proxies=PROXIES,
            timeout=60)
        response.raise_for_status()
        return response.json().get('results', [])

    return sorted({
        int(entity['features'][0]['@id'].rsplit('/', 1)[-1])
        for entity in retry_transient(fetch)})


def _process_entity(entity_id: int, mode: str) -> str:
    """Warm one entity in its own request context; return its outcome.

    The context uses the configured public base URL because the cached
    model contains absolute links.
    """
    base_url = current_app.config.get(
        'ENTITY_WARMUP_BASE_URL', 'http://127.0.0.1:5000')
    from histarchexplorer.api.presentation_view import PresentationView
    with current_app.test_request_context(base_url=base_url):
        set_api_headers()
        before = cached_at(entity_id)
        if mode == 'warm' and before is not None:
            return 'skipped'
        if mode == 'stale' and before is not None and not is_stale(before):
            return 'skipped'
        if mode == 'refresh' or is_stale(before):
            forget_entity(entity_id)
        retry_transient(lambda: PresentationView.from_api(entity_id))
        if cached_at(entity_id) is None:
            record_entity_cached(entity_id)  # adopt a legacy cache entry
            return 'skipped'
        return 'fetched'


class _Progress:
    """Thread-safe counters that write the status at most twice a second."""

    def __init__(self, tracker: JobTracker) -> None:
        self.tracker = tracker
        self.lock = threading.Lock()
        self.counts = {'processed': 0, 'fetched': 0, 'skipped': 0,
                       'failed': 0}
        self.errors: list[dict[str, Any]] = []
        self.last_write = 0.0

    def add(self, outcome: str, entity_id: int, error: str = '') -> None:
        with self.lock:
            self.counts['processed'] += 1
            self.counts[outcome] += 1
            if error and len(self.errors) < MAX_ERRORS:
                self.errors.append({'id': entity_id, 'error': error})
            self.flush()

    def flush(self, force: bool = False) -> None:
        if force or time.monotonic() - self.last_write > 0.5:
            self.last_write = time.monotonic()
            self.tracker.write(errors=self.errors, **self.counts)


def run_entity_warmup(
        tracker: JobTracker, mode: str, case_study_ids: list[int]) -> str:
    """Warm entities with two workers and a pause per API fetch.

    The pause protects the API server; skipped entities cost nothing.
    """
    app = current_app._get_current_object()  # type: ignore[attr-defined]
    delay = float(app.config.get('ENTITY_WARMUP_DELAY', 1.0))
    try:
        with app.test_request_context():
            set_api_headers()
            ids = list_entity_ids(case_study_ids)
    except Exception:
        app.logger.exception('Entity warm-up could not list entities')
        tracker.write(state='failed', finished_at=timestamp())
        return 'failed'
    (tracker.directory / 'entity-ids.json').write_text(json.dumps(ids))
    tracker.write(state='running', total=len(ids))
    progress = _Progress(tracker)

    def work(entity_id: int) -> None:
        with app.app_context():
            try:
                outcome = _process_entity(entity_id, mode)
            except Exception as error:
                app.logger.warning(
                    'Entity warm-up failed for %s: %s', entity_id, error)
                progress.add('failed', entity_id, str(error)[:200])
                return
            progress.add(outcome, entity_id)
            if outcome == 'fetched':
                time.sleep(delay)

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        list(executor.map(work, ids))
    progress.flush(force=True)
    state = 'partial' if progress.counts['failed'] else 'completed'
    tracker.write(state=state, finished_at=timestamp())
    return state


def entity_job() -> JobTracker:
    return JobTracker('entities', JOB_DEFAULTS)


def start_entity_warmup(mode: str, case_study_ids: list[int]) -> bool:
    """Start the detached warm-up; False means one is already running."""
    if mode not in MODES:
        raise ValueError(f'Unknown warm-up mode {mode!r}')
    arguments = ['--mode', mode]
    if case_study_ids:
        arguments += ['--case-studies', *map(str, case_study_ids)]
    return entity_job().start(
        'warm_entity_cache.py', arguments, {'mode': mode})


def _entity_age_stats() -> dict[str, Any]:
    """Count cached entities per age bucket (warm-up list and viewed)."""
    path = entity_job().directory / 'entity-ids.json'
    try:
        ids = json.loads(path.read_text())
    except (OSError, ValueError):
        ids = []
    try:
        ids = sorted(set(ids) | {
            int(line) for line in _seen_path().read_text().split()})
    except (OSError, ValueError):
        pass
    stamps = cache.get_many(*[_stamp_key(i) for i in ids]) if ids else []
    now = time.time()
    buckets = {name: 0 for name, _ in AGE_BUCKETS}
    buckets.update(older=0)
    cached = 0
    for stamp in stamps:
        if stamp is None:
            continue
        cached += 1
        days = (now - stamp) / SECONDS_PER_DAY
        name = next((n for n, limit in AGE_BUCKETS if days <= limit), 'older')
        buckets[name] += 1
    return {'known': len(ids), 'cached': cached, 'buckets': buckets,
            'max_age_days': max_age_seconds() / SECONDS_PER_DAY}


def _backend_stats() -> dict[str, Any]:
    """Describe the cache backend; failures only reduce the details."""
    backend = cache.cache
    stats: dict[str, Any] = {
        'type': type(backend).__name__,
        'ttl_days': round(
            float(current_app.config.get('CACHE_DEFAULT_TIMEOUT', 0))
            / SECONDS_PER_DAY, 1)}
    try:
        if hasattr(backend, '_read_client'):
            client = backend._read_client
            info = client.info()
            hits = info.get('keyspace_hits', 0)
            misses = info.get('keyspace_misses', 0)
            stats.update(
                entries=client.dbsize(),
                memory=info.get('used_memory_human', ''),
                hits=hits, misses=misses,
                hit_rate=round(100 * hits / (hits + misses))
                if hits + misses else None)
        elif hasattr(backend, '_path'):
            sizes = [entry.stat().st_size
                     for entry in os.scandir(backend._path)
                     if entry.is_file()]
            stats.update(
                entries=len(sizes),
                memory=f'{sum(sizes) / 1024 / 1024:.1f} MB')
    except Exception:
        current_app.logger.warning('Cache statistics unavailable',
                                   exc_info=True)
    return stats


def get_cache_statistics() -> dict[str, Any]:
    """Return expensive statistics, recomputed at most every two minutes."""
    stats = cache.get(STATS_KEY)
    if stats is None:
        stats = {'backend': _backend_stats(), 'entities': _entity_age_stats(),
                 'computed_at': timestamp()}
        cache.set(STATS_KEY, stats, timeout=STATS_SECONDS)
    return stats
