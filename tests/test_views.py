from flask.testing import FlaskClient
from unittest.mock import patch


def test_index(
        authenticated_client: FlaskClient) -> None:
    rv = authenticated_client.get('/')
    assert rv.status_code == 200


def test_index_redirects_unauthenticated(
        client: FlaskClient) -> None:
    rv = client.get('/')
    assert rv.status_code == 302


def test_set_language(authenticated_client: FlaskClient) -> None:
    rv = authenticated_client.get('/language=de', headers={'Referer': '/'}, follow_redirects=True)
    assert rv.status_code == 200


def test_set_language_no_referer(client: FlaskClient) -> None:
    rv = client.get('/language=en')
    # If no referer, it might redirect to index or fail depending on Flask version/config
    assert rv.status_code in (302, 200)


def test_type_tree(
        authenticated_client: FlaskClient) -> None:
    with patch('histarchexplorer.api.api_access.ApiAccess.get_type_tree',
               return_value={'tree': []}):
        rv = authenticated_client.get('/type-tree')
        assert rv.status_code == 200


def test_files_of_entities(
        authenticated_client: FlaskClient) -> None:
    with patch('histarchexplorer.api.api_access.ApiAccess.get_files_of_entities',
               return_value=[]):
        rv = authenticated_client.get('/files-of-entities')
        assert rv.status_code == 200


def test_entities_count(
        authenticated_client: FlaskClient) -> None:
    with patch('histarchexplorer.api.api_access.ApiAccess.get_entities_count_by_case_studies',
               return_value={}):
        rv = authenticated_client.get('/entities-count')
        assert rv.status_code == 200


def test_refresh_cache(authenticated_client: FlaskClient) -> None:
    rv = authenticated_client.get('/refresh-cache/1')
    assert rv.status_code == 302
    assert '/entity/1' in rv.location


def test_refresh_cache_error(authenticated_client: FlaskClient) -> None:
    with patch('histarchexplorer.cache.delete_memoized',
               side_effect=Exception("Test Error")):
        rv = authenticated_client.get('/refresh-cache/1')
        assert rv.status_code == 500
        assert b"Test Error" in rv.data
