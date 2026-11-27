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


@pytest.fixture(autouse=True)
def clear_case_studies_cache():
    cache.delete_memoized(ApiAccess.get_case_studies)
    yield
    cache.delete_memoized(ApiAccess.get_case_studies)


@pytest.mark.parametrize('base_url', [
    'https://example.test/api/', 'https://example.test/api',
    'https://example.test/api/1/', 'https://example.test/api/1'])
def test_get_case_studies_fetches_and_caches(monkeypatch, base_url):
    monkeypatch.setitem(app.config, 'API_URL', base_url)
    payload_data = [
        {
            'id': 181731,
            'name': 'THANADOS',
            'description': 'Desc',
            'uuid': '9f343109-71af-435c-884d-f6698b3022ea',
            'subCaseStudies': [{
                'id': 239427,
                'name': 'FMA Tir-Vbg',
                'description': None,
                'uuid': '53ef0923-62dd-4bb7-89b1-0810431d681a',
                'subCaseStudies': []}]}]
    response = MagicMock()
    response.json.return_value = {'data': payload_data}
    with app.test_request_context():
        g.api_headers = {'Authorization': 'Bearer test'}
        with patch('histarchexplorer.api.api_access.requests.get',
                   return_value=response) as mock_get:
            assert ApiAccess.get_case_studies() == payload_data
            assert ApiAccess.get_case_studies() == payload_data

    mock_get.assert_called_once_with(
        'https://example.test/api/1/case-studies',
        headers={'Authorization': 'Bearer test'},
        proxies=PROXIES,
        timeout=30)
    response.raise_for_status.assert_called_once_with()


@pytest.mark.parametrize('bad_payload', [
    [], 'invalid', {}, {'data': 'not-a-list'}])
def test_get_case_studies_rejects_bad_payload_and_does_not_cache(bad_payload):
    bad_response = MagicMock()
    bad_response.json.return_value = bad_payload
    good_response = MagicMock()
    good_response.json.return_value = {'data': [{'id': 8241, 'name': 'CS'}]}

    with app.test_request_context():
        g.api_headers = {}
        with patch('histarchexplorer.api.api_access.requests.get',
                   side_effect=[bad_response, good_response]) as mock_get:
            with pytest.raises(ValueError):
                ApiAccess.get_case_studies()
            assert ApiAccess.get_case_studies() == [{'id': 8241, 'name': 'CS'}]

    assert mock_get.call_count == 2


def test_get_case_study_fetches_by_id(monkeypatch):
    monkeypatch.setitem(app.config, 'API_URL', 'https://example.test/api/')
    payload = {
        'id': 181731,
        'name': 'THANADOS',
        'subCaseStudies': [],
        'uuid': '9f343109-71af-435c-884d-f6698b3022ea'}
    response = MagicMock()
    response.status_code = 200
    response.json.return_value = payload

    with app.test_request_context():
        g.api_headers = {'Authorization': 'Bearer test'}
        with patch('histarchexplorer.api.api_access.requests.get',
                   return_value=response) as mock_get:
            assert ApiAccess.get_case_study(181731) == payload

    mock_get.assert_called_once_with(
        'https://example.test/api/1/case-studies/181731',
        headers={'Authorization': 'Bearer test'},
        proxies=PROXIES,
        timeout=30)


def test_get_case_study_returns_none_on_404():
    response = MagicMock()
    response.status_code = 404
    with app.test_request_context():
        g.api_headers = {}
        with patch('histarchexplorer.api.api_access.requests.get',
                   return_value=response):
            assert ApiAccess.get_case_study(8240) is None
    response.raise_for_status.assert_not_called()


@pytest.mark.parametrize('invalid_id', [0, -1, True, '42'])
def test_get_case_study_rejects_invalid_ids(invalid_id):
    with app.test_request_context():
        with patch('histarchexplorer.api.api_access.requests.get') as mock_get:
            with pytest.raises(ValueError):
                ApiAccess.get_case_study(invalid_id)
    mock_get.assert_not_called()


@pytest.mark.parametrize('bad_payload', [[], 'invalid', {'name': 'No ID'}])
def test_get_case_study_rejects_invalid_payload(bad_payload):
    response = MagicMock()
    response.status_code = 200
    response.json.return_value = bad_payload
    with app.test_request_context():
        g.api_headers = {}
        with patch('histarchexplorer.api.api_access.requests.get',
                   return_value=response):
            with pytest.raises(ValueError):
                ApiAccess.get_case_study(181731)


def test_flatten_case_studies():
    from histarchexplorer.utils.view_util import flatten_case_studies
    tree = [
        {'id': 8241, 'name': 'Root A', 'subCaseStudies': []},
        {
            'id': 181731,
            'name': 'THANADOS',
            'subCaseStudies': [
                {
                    'id': 239427,
                    'name': 'FMA Tir-Vbg',
                    'subCaseStudies': [
                        {'id': 999, 'name': 'Deep', 'subCaseStudies': []}]}]}]
    with app.test_request_context():
        assert flatten_case_studies(tree) == [
            {'id': 8241, 'name': 'Root A'},
            {'id': 181731, 'name': 'THANADOS'},
            {'id': 239427, 'name': '- FMA Tir-Vbg'},
            {'id': 999, 'name': '-- Deep'}]


@pytest.fixture(autouse=True)
def clear_entity_counts_cache():
    cache.delete_memoized(ApiAccess.get_system_class_count)
    yield
    cache.delete_memoized(ApiAccess.get_system_class_count)


@pytest.mark.parametrize('base_url', [
    'https://example.test/api/', 'https://example.test/api',
    'https://example.test/api/1/', 'https://example.test/api/1'])
def test_get_entities_count_multiple_case_studies_and_caches(
        monkeypatch, base_url):
    monkeypatch.setitem(app.config, 'API_URL', base_url)
    response = MagicMock()
    response.json.return_value = {'counts': {'place': 10, 'artifact': 25}}
    with app.test_request_context():
        g.api_headers = {'Authorization': 'Bearer test'}
        g.case_study_ids = [181731, 221174]
        with patch('histarchexplorer.api.api_access.requests.get',
                   return_value=response) as mock_get:
            expected = {'place': 10, 'artifact': 25}
            assert ApiAccess.get_entities_count_by_case_studies() == expected
            assert ApiAccess.get_entities_count_by_case_studies(
                [181731, 221174]) == expected
            assert ApiAccess.get_system_class_count(
                (181731, 221174)) == expected

    mock_get.assert_called_once_with(
        'https://example.test/api/1/system/count/entities',
        params={'caseStudy': [181731, 221174]},
        headers={'Authorization': 'Bearer test'},
        proxies=PROXIES,
        timeout=30)
    response.raise_for_status.assert_called_once_with()


def test_get_entities_count_single_int_and_list_share_cache(monkeypatch):
    monkeypatch.setitem(app.config, 'API_URL', 'https://example.test/api/')
    response = MagicMock()
    response.json.return_value = {'counts': {'place': 5}}
    with app.test_request_context():
        g.api_headers = {}
        g.case_study_ids = []
        with patch('histarchexplorer.api.api_access.requests.get',
                   return_value=response) as mock_get:
            assert ApiAccess.get_entities_count_by_case_studies(
                181731) == {'place': 5}
            assert ApiAccess.get_entities_count_by_case_studies(
                [181731]) == {'place': 5}

    mock_get.assert_called_once_with(
        'https://example.test/api/1/system/count/entities',
        params={'caseStudy': [181731]},
        headers={},
        proxies=PROXIES,
        timeout=30)


@pytest.mark.parametrize('arg', [None, 0, []])
def test_get_entities_count_falls_back_and_allows_empty(monkeypatch, arg):
    monkeypatch.setitem(app.config, 'API_URL', 'https://example.test/api/')
    response = MagicMock()
    response.json.return_value = {'counts': {'place': 99}}
    with app.test_request_context():
        g.api_headers = {}
        g.case_study_ids = []
        with patch('histarchexplorer.api.api_access.requests.get',
                   return_value=response) as mock_get:
            assert ApiAccess.get_entities_count_by_case_studies(
                arg) == {'place': 99}

    mock_get.assert_called_once_with(
        'https://example.test/api/1/system/count/entities',
        params={},
        headers={},
        proxies=PROXIES,
        timeout=30)


@pytest.mark.parametrize('bad_payload', [[], {}, {'counts': []}])
def test_get_entities_count_rejects_bad_payload_without_caching(bad_payload):
    bad_response = MagicMock()
    bad_response.json.return_value = bad_payload
    good_response = MagicMock()
    good_response.json.return_value = {'counts': {'place': 7}}

    with app.test_request_context():
        g.api_headers = {}
        with patch('histarchexplorer.api.api_access.requests.get',
                   side_effect=[bad_response, good_response]) as mock_get:
            with pytest.raises(ValueError):
                ApiAccess.get_system_class_count((181731,))
            assert ApiAccess.get_system_class_count((181731,)) == {'place': 7}

    assert mock_get.call_count == 2


def test_get_type_descendant_ids_empty_skips_api():
    with patch.object(ApiAccess, 'get_vocabulary_tree') as mock_tree:
        assert ApiAccess.get_type_descendant_ids([]) == []
    mock_tree.assert_not_called()


def test_get_type_descendant_ids_collects_and_deduplicates():
    tree = {
        'standard': [{
            'id': 10,
            'children': [
                {'id': 11, 'children': [{'id': 12, 'children': []}]},
                {'id': 13, 'children': []}]}],
        'custom': [{'id': 20, 'children': []}]}
    with patch.object(ApiAccess, 'get_vocabulary_tree', return_value=tree):
        assert ApiAccess.get_type_descendant_ids([10, 11, 999]) == [
            10, 11, 12, 13, 999]


def test_get_type_descendant_ids_falls_back_on_error():
    with patch.object(
            ApiAccess,
            'get_vocabulary_tree',
            side_effect=requests.RequestException('down')):
        assert ApiAccess.get_type_descendant_ids([10, 10, 20]) == [10, 20]


def test_get_p46_child_ids_extracts_children():
    payload = {
        '111285': [
            {'id': 111285, 'children': [111289, 116170, 111289]},
            {'id': 116170, 'children': [200]}]}
    with patch.object(ApiAccess, 'get_subunits', return_value=payload):
        assert ApiAccess.get_p46_child_ids(111285) == [111289, 116170]
        assert ApiAccess.get_p46_child_ids(116170) == []


def test_get_p46_child_ids_handles_feature_and_errors():
    payload = {'50705': [{'id': 50705, 'children': [78767]}]}
    with patch.object(ApiAccess, 'get_subunits', return_value=payload):
        assert ApiAccess.get_p46_child_ids(50705) == [78767]

    for err in (requests.HTTPError('400'), ValueError('bad json')):
        with patch.object(ApiAccess, 'get_subunits', side_effect=err):
            assert ApiAccess.get_p46_child_ids(369688) == []

    with patch.object(ApiAccess, 'get_subunits', return_value=['bad']):
        assert ApiAccess.get_p46_child_ids(111285) == []

    for invalid_id in (0, -1, True):
        with patch.object(ApiAccess, 'get_subunits') as mock_sub:
            assert ApiAccess.get_p46_child_ids(invalid_id) == []
            mock_sub.assert_not_called()


@pytest.fixture(autouse=True)
def clear_map_overlays_cache():
    cache.delete_memoized(ApiAccess.get_map_overlays)
    yield
    cache.delete_memoized(ApiAccess.get_map_overlays)


def test_get_map_overlays_paginates_deduplicates_and_caches(monkeypatch):
    monkeypatch.setitem(app.config, 'API_URL', 'https://example.test/api/')
    page1 = MagicMock()
    page1.json.return_value = {
        'data': [
            {
                'id': 41011,
                'name': 'Plan A',
                'bounds': [[47.4, 15.0], [47.5, 15.1]],
                'iiifBaseUrl': 'https://iiif.example/41011.png',
                'extension': 'png',
                'fileUrl': 'https://example.test/api/1/files/41011/display'},
            {
                'id': 999,
                'name': 'No Bounds',
                'bounds': None}],
        'next': 'https://example.test/api/1/files/overlays?page=2'}
    page2 = MagicMock()
    page2.json.return_value = {
        'data': [
            {
                'id': 41011,
                'name': 'Duplicate',
                'bounds': [[47.4, 15.0], [47.5, 15.1]]},
            {
                'id': 41762,
                'name': 'Plan B',
                'bounds': [[48.0, 16.7], [48.1, 16.8], [47.9, 16.7]],
                'iiifBaseUrl': None,
                'extension': 'jpg',
                'fileUrl': 'https://example.test/api/1/files/41762/display'}],
        'next': None}

    with app.test_request_context():
        g.api_headers = {'Authorization': 'Bearer test'}
        with patch('histarchexplorer.api.api_access.requests.get',
                   side_effect=[page1, page2]) as mock_get:
            expected = [
                {
                    'id': 41011,
                    'name': 'Plan A',
                    'bbox': [[47.4, 15.0], [47.5, 15.1]],
                    'iiif_base_url': 'https://iiif.example/41011.png',
                    'extension': 'png',
                    'file_url': (
                        'https://example.test/api/1/files/41011/display')},
                {
                    'id': 41762,
                    'name': 'Plan B',
                    'bbox': [[48.0, 16.7], [48.1, 16.8], [47.9, 16.7]],
                    'iiif_base_url': None,
                    'extension': 'jpg',
                    'file_url': (
                        'https://example.test/api/1/files/41762/display')}]
            assert ApiAccess.get_map_overlays() == expected
            assert ApiAccess.get_map_overlays() == expected

    assert mock_get.call_count == 2
    assert mock_get.call_args_list[0].kwargs['params'] == {
        'limit': 100, 'page': 1}
    assert mock_get.call_args_list[1].kwargs['params'] == {
        'limit': 100, 'page': 2}


def test_get_map_overlays_stops_on_empty_data():
    response = MagicMock()
    response.json.return_value = {'data': [], 'next': 'https://next'}
    with app.test_request_context():
        g.api_headers = {}
        with patch('histarchexplorer.api.api_access.requests.get',
                   return_value=response) as mock_get:
            assert ApiAccess.get_map_overlays() == []
    mock_get.assert_called_once()


@pytest.mark.parametrize('bad_payload', [[], {}, {'data': 'bad'}])
def test_get_map_overlays_rejects_bad_payload_without_caching(bad_payload):
    bad_response = MagicMock()
    bad_response.json.return_value = bad_payload
    good_response = MagicMock()
    good_response.json.return_value = {'data': [], 'next': None}
    with app.test_request_context():
        g.api_headers = {}
        with patch('histarchexplorer.api.api_access.requests.get',
                   side_effect=[bad_response, good_response]) as mock_get:
            with pytest.raises(ValueError):
                ApiAccess.get_map_overlays()
            assert ApiAccess.get_map_overlays() == []
    assert mock_get.call_count == 2
