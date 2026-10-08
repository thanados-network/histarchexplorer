"""Entity cache tests need no database, real subprocesses or external API."""

import os
import time
from unittest.mock import patch

import pytest
from flask_caching.backends import FileSystemCache

from histarchexplorer import app, cache
from histarchexplorer.api.presentation_view import PresentationView
from histarchexplorer.services import entity_cache as entities
from histarchexplorer.services.cache_jobs import JobTracker

DAY = 86400


@pytest.fixture(scope='session', autouse=True)
def setup_database():
    """These application-context-only tests deliberately need no database."""
    yield


@pytest.fixture()
def isolated(tmp_path, monkeypatch):
    backend = FileSystemCache(str(tmp_path / 'cache'), default_timeout=1234)
    monkeypatch.setitem(app.extensions['cache'], cache, backend)
    monkeypatch.setitem(app.config, 'CACHE_JOBS_DIR', str(tmp_path / 'jobs'))
    monkeypatch.setitem(app.config, 'ENTITY_WARMUP_DELAY', 0)
    monkeypatch.setattr(
        entities, 'forget_entity',
        lambda entity_id: cache.delete(f'entity_cached_at:{entity_id}'))
    with app.app_context():
        yield backend


def fake_fetch(calls):
    def fetch(entity_id):
        calls.append(entity_id)
        entities.record_entity_cached(entity_id)
    return fetch


def test_stamp_and_staleness(isolated):
    assert entities.cached_at(1) is None
    assert not entities.is_stale(None)
    entities.record_entity_cached(1)
    assert not entities.is_stale(entities.cached_at(1))
    cache.set('entity_cached_at:1', time.time() - 8 * DAY)
    assert entities.is_stale(entities.cached_at(1))


def test_ensure_fresh_forgets_only_stale_entries(isolated):
    cache.set('entity_cached_at:1', time.time() - 8 * DAY)
    entities.record_entity_cached(2)
    with patch.object(entities, 'forget_entity') as forget:
        entities.ensure_entity_fresh(1)
        entities.ensure_entity_fresh(2)
        entities.ensure_entity_fresh(3)
    forget.assert_called_once_with(1)


@pytest.mark.parametrize(('mode', 'age_days', 'expected'), [
    ('warm', None, ['fetch']),
    ('warm', 30, ['skip']),
    ('stale', 1, ['skip']),
    ('stale', 30, ['fetch']),
    ('refresh', 1, ['fetch'])])
def test_modes_decide_what_to_fetch(isolated, mode, age_days, expected):
    calls = []
    if age_days is not None:
        cache.set('entity_cached_at:7', time.time() - age_days * DAY)
    with patch.object(PresentationView, 'from_api',
                      side_effect=fake_fetch(calls)):
        outcome = entities._process_entity(7, mode)
    assert [{'fetched': 'fetch', 'skipped': 'skip'}[outcome]] == expected
    assert bool(calls) == (expected == ['fetch'])


def test_legacy_entry_is_adopted_without_fetching(isolated):
    with patch.object(PresentationView, 'from_api'):
        assert entities._process_entity(7, 'refresh') == 'skipped'
    assert entities.cached_at(7) is not None


def test_warmup_counts_outcomes_and_errors(isolated):
    tracker = entities.entity_job()

    def process(entity_id, mode):
        if entity_id == 2:
            raise RuntimeError('boom')
        return 'fetched' if entity_id == 1 else 'skipped'

    with patch.object(entities, 'list_entity_ids', return_value=[1, 2, 3]), \
            patch.object(entities, '_process_entity', side_effect=process):
        state = entities.run_entity_warmup(tracker, 'warm', [])
    status = tracker.read()
    assert state == status['state'] == 'partial'
    assert (status['total'], status['processed'], status['fetched'],
            status['skipped'], status['failed']) == (3, 3, 1, 1, 1)
    assert status['errors'] == [{'id': 2, 'error': 'boom'}]
    stats = entities._entity_age_stats()
    assert stats['known'] == 3


def test_warmup_fails_when_listing_fails(isolated):
    tracker = entities.entity_job()
    with patch.object(entities, 'list_entity_ids', side_effect=OSError):
        assert entities.run_entity_warmup(tracker, 'warm', []) == 'failed'
    assert tracker.read()['state'] == 'failed'


def test_age_statistics_group_entries(isolated):
    tracker = entities.entity_job()
    (tracker.directory / 'entity-ids.json').write_text('[1, 2, 3, 4]')
    for entity_id, age in ((1, 0.5), (2, 2), (3, 30)):
        cache.set(f'entity_cached_at:{entity_id}', time.time() - age * DAY)
    stats = entities._entity_age_stats()
    assert stats['known'] == 4
    assert stats['cached'] == 3
    assert stats['buckets'] == {
        'day': 1, 'three_days': 1, 'week': 0, 'older': 1}


def test_dead_worker_is_reported_interrupted(isolated):
    tracker = entities.entity_job()
    tracker.write(state='running')
    assert tracker.status()['state'] == 'interrupted'


def test_running_job_is_not_started_twice(isolated):
    tracker = entities.entity_job()
    fd = tracker.lock()
    try:
        with patch('subprocess.Popen') as popen:
            assert not entities.start_entity_warmup('warm', [])
        popen.assert_not_called()
    finally:
        os.close(fd)


def test_start_launches_detached_worker(isolated):
    with patch('subprocess.Popen') as popen:
        assert entities.start_entity_warmup('stale', [3, 4])
    arguments = popen.call_args.args[0]
    assert arguments[1].endswith('warm_entity_cache.py')
    assert arguments[-5:] == ['--mode', 'stale', '--case-studies', '3', '4']
    assert popen.call_args.kwargs['start_new_session']
    assert entities.entity_job().read()['state'] == 'queued'


def test_unknown_mode_is_rejected(isolated):
    with pytest.raises(ValueError):
        entities.start_entity_warmup('everything', [])


def test_statistics_describe_backend(isolated):
    stats = entities.get_cache_statistics()
    assert stats['backend']['type'] == 'FileSystemCache'
    assert stats is not None and 'entities' in stats


def test_job_tracker_defaults_for_missing_file(isolated):
    tracker = JobTracker('unknown', {'state': 'idle'})
    assert tracker.status() == {'state': 'idle'}
