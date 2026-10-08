from unittest.mock import MagicMock, patch

import pytest
import requests
from flask import g

from histarchexplorer import app, cache
from histarchexplorer.api.api_access import ApiAccess, PROXIES


@pytest.fixture(autouse=True)
def clear_subunits_cache():
    cache.delete_memoized(ApiAccess.get_subunits)
    yield
    cache.delete_memoized(ApiAccess.get_subunits)


def test_get_subunits_fetches_and_caches_hierarchy():
    response = MagicMock()
    response.json.return_value = {'features': []}
    with app.test_request_context():
        g.api_headers = {'Authorization': 'Bearer test'}
        with patch('histarchexplorer.api.api_access.requests.get',
                   return_value=response) as mock_get:
            assert ApiAccess.get_subunits(50505) == {'features': []}
            assert ApiAccess.get_subunits(50505) == {'features': []}

    mock_get.assert_called_once_with(
        f"{app.config['API_URL']}subunits/50505",
        headers={'Authorization': 'Bearer test'},
        proxies=PROXIES,
        timeout=60)
    response.raise_for_status.assert_called_once_with()


def test_get_subunits_raises_for_failed_response():
    response = MagicMock()
    response.raise_for_status.side_effect = requests.HTTPError('not found')
    with app.test_request_context():
        g.api_headers = {}
        with patch('histarchexplorer.api.api_access.requests.get',
                   return_value=response):
            with pytest.raises(requests.HTTPError):
                ApiAccess.get_subunits(50505)
    response.json.assert_not_called()


@pytest.fixture(autouse=True)
def clear_vocabulary_cache():
    methods = (ApiAccess.get_vocabulary_tree,
               ApiAccess.get_vocabulary_detail)
    for method in methods:
        cache.delete_memoized(method)
    yield
    for method in methods:
        cache.delete_memoized(method)


@pytest.fixture(params=['tree', 'detail'])
def vocabulary_fetch(request):
    if request.param == 'tree':
        return ApiAccess.get_vocabulary_tree, (), 'tree'
    return ApiAccess.get_vocabulary_detail, (42,), '42'


@pytest.mark.parametrize('base_url', [
    'https://example.test/api/', 'https://example.test/api',
    'https://example.test/api/1/', 'https://example.test/api/1'])
def test_vocabulary_url_and_request_options(
        vocabulary_fetch, monkeypatch, base_url):
    fetch, args, endpoint = vocabulary_fetch
    monkeypatch.setitem(app.config, 'API_URL', base_url)
    response = MagicMock()
    response.json.return_value = {'id': 42, 'children': []}
    headers = {'Authorization': 'Bearer test'}
    with app.test_request_context():
        g.api_headers = headers
        with patch('histarchexplorer.api.api_access.requests.get',
                   return_value=response) as mock_get:
            assert fetch(*args) == response.json.return_value

    mock_get.assert_called_once_with(
        f'https://example.test/api/1/vocabulary/{endpoint}',
        headers=headers, proxies=PROXIES, timeout=60)
    response.raise_for_status.assert_called_once_with()


def test_vocabulary_preserves_and_caches_payload(vocabulary_fetch):
    fetch, args, _ = vocabulary_fetch
    payload = {
        'id': 42, 'label': 'Gräber', 'parent': None,
        'children': [{'id': 43, 'metadata': {'custom': True}}],
        'unknown': ['kept', 0]}
    response = MagicMock()
    response.json.return_value = payload
    with app.test_request_context():
        g.api_headers = {}
        with patch('histarchexplorer.api.api_access.requests.get',
                   return_value=response) as mock_get:
            assert fetch(*args) == payload
            assert fetch(*args) == payload

    mock_get.assert_called_once()
    response.raise_for_status.assert_called_once_with()
    response.json.assert_called_once_with()


def test_vocabulary_detail_cache_is_separate_for_each_id():
    responses = [MagicMock(), MagicMock()]
    responses[0].json.return_value = {'id': 42}
    responses[1].json.return_value = {'id': 43}
    with app.test_request_context():
        g.api_headers = {}
        with patch('histarchexplorer.api.api_access.requests.get',
                   side_effect=responses) as mock_get:
            for id_ in (42, 43, 42, 43):
                assert ApiAccess.get_vocabulary_detail(id_) == {'id': id_}

    assert mock_get.call_count == 2


@pytest.mark.parametrize('id_', [
    0, -1, '42', 'tree', 1.5, 42.0, None, True, False])
def test_vocabulary_detail_rejects_non_positive_integer_ids(id_):
    with app.test_request_context():
        g.api_headers = {}
        with patch('histarchexplorer.api.api_access.requests.get') as mock_get:
            with pytest.raises(ValueError):
                ApiAccess.get_vocabulary_detail(id_)
    mock_get.assert_not_called()


@pytest.mark.parametrize('failure', [
    'http', 'timeout', 'request', 'json', 'list', 'null', 'string'])
def test_vocabulary_errors_are_not_cached(vocabulary_fetch, failure):
    fetch, args, _ = vocabulary_fetch
    bad_response = MagicMock()
    good_response = MagicMock()
    good_response.json.return_value = {'id': 42}
    expected_error = ValueError
    if failure == 'http':
        expected_error = requests.HTTPError
        bad_response.raise_for_status.side_effect = expected_error('failed')
    elif failure == 'json':
        bad_response.json.side_effect = ValueError('invalid JSON')
    else:
        bad_response.json.return_value = {
            'list': [], 'null': None, 'string': 'invalid'}.get(failure)
    first_result = bad_response
    if failure in ('timeout', 'request'):
        expected_error = (requests.Timeout if failure == 'timeout'
                          else requests.RequestException)
        first_result = expected_error('failed')

    with app.test_request_context():
        g.api_headers = {}
        with patch('histarchexplorer.api.api_access.requests.get',
                   side_effect=[first_result, good_response]) as mock_get:
            with pytest.raises(expected_error):
                fetch(*args)
            assert fetch(*args) == {'id': 42}
            assert fetch(*args) == {'id': 42}

    assert mock_get.call_count == 2
    if failure == 'http':
        bad_response.json.assert_not_called()