from unittest.mock import MagicMock, patch

import pytest
import requests

from histarchexplorer import app, cache
from histarchexplorer.api.api_access import ApiAccess
from histarchexplorer.models.settings import Settings


@pytest.fixture(autouse=True)
def vocabulary_settings_and_cache():
    methods = (ApiAccess.get_vocabulary_tree,
               ApiAccess.get_vocabulary_detail)
    for method in methods:
        cache.delete_memoized(method)
    settings = Settings()
    settings.access_restriction = False
    with patch.object(Settings, 'load_from_db', return_value=settings):
        yield settings
    for method in methods:
        cache.delete_memoized(method)


@pytest.fixture(params=['tree', '42'])
def vocabulary_url(request):
    return f'/api/vocabulary/{request.param}'


def test_vocabulary_routes_preserve_and_cache_json(client, vocabulary_url):
    payload = {
        'id': 42, 'label': 'Gräber', 'parent': None,
        'children': [{'id': 43, 'extra': True}], 'unknown': ['kept']}
    response = MagicMock()
    response.json.return_value = payload
    with patch('histarchexplorer.api.api_access.requests.get',
               return_value=response) as mock_get:
        for _ in range(2):
            result = client.get(vocabulary_url)
            assert result.status_code == 200
            assert result.is_json
            assert result.get_json() == payload

    mock_get.assert_called_once()
    response.raise_for_status.assert_called_once_with()


@pytest.mark.parametrize('status', [404, 400, 401, 403, 500, None])
def test_vocabulary_http_errors_are_safe(
        client, vocabulary_url, status):
    upstream = requests.Response() if status is not None else None
    if upstream is not None:
        upstream.status_code = status
    error = requests.HTTPError(
        'Bearer secret-token at https://private.example/api',
        response=upstream)
    response = MagicMock()
    response.json.return_value = {'id': 42}
    with patch('histarchexplorer.api.api_access.requests.get',
               side_effect=[error, response]) as mock_get:
        result = client.get(vocabulary_url)
        retry = client.get(vocabulary_url)

    assert result.status_code == (404 if status == 404 else 502)
    assert result.is_json
    assert result.get_json() == {'error': 'Vocabulary data unavailable.'}
    assert b'secret-token' not in result.data
    assert b'private.example' not in result.data
    assert retry.status_code == 200
    assert retry.get_json() == {'id': 42}
    assert mock_get.call_count == 2


@pytest.mark.parametrize('failure', ['json', 'list', 'null'])
def test_vocabulary_invalid_payloads_are_safe_and_retryable(
        client, vocabulary_url, failure):
    bad_response = MagicMock()
    if failure == 'json':
        bad_response.json.side_effect = ValueError('secret upstream body')
    else:
        bad_response.json.return_value = [] if failure == 'list' else None
    good_response = MagicMock()
    good_response.json.return_value = {'id': 42}
    with patch('histarchexplorer.api.api_access.requests.get',
               side_effect=[bad_response, good_response]) as mock_get:
        result = client.get(vocabulary_url)
        retry = client.get(vocabulary_url)

    assert result.status_code == 502
    assert result.is_json
    assert result.get_json() == {'error': 'Vocabulary data unavailable.'}
    assert b'secret upstream body' not in result.data
    assert retry.status_code == 200
    assert retry.get_json() == {'id': 42}
    assert mock_get.call_count == 2


@pytest.mark.parametrize('error_type, status', [
    (requests.Timeout, 504), (requests.ConnectionError, 502),
    (requests.RequestException, 502), (ValueError, 502)])
def test_vocabulary_errors_are_safe_and_retryable(
        client, vocabulary_url, error_type, status):
    error = error_type('Bearer secret-token at https://private.example/api')
    response = MagicMock()
    response.json.return_value = {'id': 42}
    with patch('histarchexplorer.api.api_access.requests.get',
               side_effect=[error, response]) as mock_get:
        result = client.get(vocabulary_url)
        assert result.status_code == status
        assert result.is_json
        message = ('Vocabulary service timed out.' if status == 504
                   else 'Vocabulary data unavailable.')
        assert result.get_json() == {'error': message}
        assert b'secret-token' not in result.data
        assert b'private.example' not in result.data
        retry = client.get(vocabulary_url)
        assert retry.status_code == 200
        assert retry.get_json() == {'id': 42}

    assert mock_get.call_count == 2


@pytest.mark.parametrize('path', ['0', '-1', '1.5', 'not-an-id'])
def test_vocabulary_invalid_ids_do_not_fetch(client, path):
    with patch.object(ApiAccess, 'get_vocabulary_detail') as mock_fetch:
        result = client.get(f'/api/vocabulary/{path}')
    assert result.status_code == 404
    mock_fetch.assert_not_called()
    if path == '0':
        assert result.get_json() == {'error': 'Vocabulary type not found.'}


def test_vocabulary_obeys_global_access_restriction(
        client, vocabulary_url, vocabulary_settings_and_cache):
    vocabulary_settings_and_cache.access_restriction = True
    with patch('histarchexplorer.api.api_access.requests.get') as mock_get:
        result = client.get(vocabulary_url)

    assert result.status_code == 302
    assert result.headers['Location'].endswith('/login')
    mock_get.assert_not_called()


def test_vocabulary_allows_authenticated_restricted_access(
        authenticated_client, vocabulary_url, vocabulary_settings_and_cache):
    vocabulary_settings_and_cache.access_restriction = True
    response = MagicMock()
    response.json.return_value = {'id': 42}
    with patch('histarchexplorer.api.api_access.requests.get',
               return_value=response) as mock_get:
        result = authenticated_client.get(vocabulary_url)

    assert result.status_code == 200
    assert result.get_json() == {'id': 42}
    mock_get.assert_called_once()


@pytest.mark.parametrize('include, exclude, expected', [
    ('42, 43,42', '', ([42, 43], [])),
    ('', '42,42', ([], [42])), ('', '', ([], []))])
def test_admin_saves_vocabulary_filters(
        authenticated_client, vocabulary_settings_and_cache,
        include, exclude, expected):
    settings = vocabulary_settings_and_cache
    settings.hidden_ids = [999]
    with patch.object(Settings, 'save_to_db') as save:
        response = authenticated_client.post(
            '/admin/update_vocabulary_settings',
            data={'include_ids': include, 'exclude_ids': exclude})
    assert response.status_code == 302
    assert response.location.endswith('/admin/sidebar-vocabulary-settings')
    assert (settings.vocabulary_include_ids,
            settings.vocabulary_exclude_ids) == expected
    assert settings.hidden_ids == [999]
    save.assert_called_once()


@pytest.mark.parametrize('title', ['', 'My vocabulary', '  Gräber & Funde  '])
def test_admin_saves_vocabulary_title(
        authenticated_client, vocabulary_settings_and_cache, title):
    with patch.object(Settings, 'save_to_db') as save:
        response = authenticated_client.post(
            '/admin/update_vocabulary_settings',
            data={'title': title})
    assert response.status_code == 302
    assert vocabulary_settings_and_cache.vocabulary_title == title.strip()
    save.assert_called_once()


@pytest.mark.parametrize('title', ['', 'Gräber & "Funde" <script>'])
def test_vocabulary_title_attribute(
        client, vocabulary_settings_and_cache, title):
    from html.parser import HTMLParser

    class WidgetParser(HTMLParser):
        attributes = {}

        def handle_starttag(self, tag, attrs):
            if tag == 'openatlas-vocabulary-viewer':
                self.attributes = dict(attrs)

    vocabulary_settings_and_cache.vocabulary_title = title
    response = client.get('/vocabulary')
    parser = WidgetParser()
    html = response.get_data(as_text=True)
    parser.feed(html)
    if title:
        assert parser.attributes['header-title'] == title
        widget = html.split('<openatlas-vocabulary-viewer', 1)[1].split(
            '</openatlas-vocabulary-viewer>', 1)[0]
        assert '&lt;script&gt;' in widget
        assert '<script>' not in widget
    else:
        assert 'header-title' not in parser.attributes


def test_admin_displays_vocabulary_title(
        authenticated_client, vocabulary_settings_and_cache):
    vocabulary_settings_and_cache.vocabulary_title = 'Custom & "Title"'
    response = authenticated_client.get('/admin/sidebar-vocabulary-settings')
    html = response.get_data(as_text=True)
    assert 'name="title"' in html
    assert 'Custom &amp; &#34;Title&#34;' in html


@pytest.mark.parametrize('include, exclude', [
    ('1', '2'), ('-1', ''), ('0', ''), ('1.5', ''), ('abc', ''),
    ('1,,2', ''), ('', 'true'), ('', '1,'), ('١', '')])
def test_admin_rejects_invalid_vocabulary_filters(
        authenticated_client, vocabulary_settings_and_cache,
        include, exclude):
    settings = vocabulary_settings_and_cache
    settings.vocabulary_include_ids = [42]
    settings.vocabulary_title = 'Original title'
    with patch.object(Settings, 'save_to_db') as save:
        response = authenticated_client.post(
            '/admin/update_vocabulary_settings',
            data={'include_ids': include, 'exclude_ids': exclude,
                  'title': 'Changed title'})
    assert response.status_code == 302
    assert settings.vocabulary_include_ids == [42]
    assert settings.vocabulary_exclude_ids == []
    assert settings.vocabulary_title == 'Original title'
    save.assert_not_called()
    with authenticated_client.session_transaction() as session:
        assert any('positive, comma-separated IDs' in text
                   for _, text in session['_flashes'])


@pytest.mark.parametrize('group, status', [
    ('admin', 302), ('manager', 302), ('user', 403)])
def test_vocabulary_admin_role_protection(client, group, status):
    user = MagicMock(is_authenticated=True, group=group)
    with patch('flask_login.utils._get_user', return_value=user), \
            patch.object(Settings, 'save_to_db') as save:
        response = client.post('/admin/update_vocabulary_settings')
    assert response.status_code == status
    assert save.call_count == (1 if status == 302 else 0)


def test_vocabulary_admin_requires_login(client):
    with patch.object(Settings, 'save_to_db') as save:
        response = client.post('/admin/update_vocabulary_settings')
    assert response.status_code == 302
    assert '/login' in response.location
    save.assert_not_called()


@pytest.mark.parametrize('page_type', ['default', 'individual'])
def test_vocabulary_menu_page_type(
        authenticated_client, vocabulary_settings_and_cache, page_type):
    with patch.object(Settings, 'save_to_db'):
        response = authenticated_client.post(
            '/admin/update_menu_management',
            data={'show_vocabulary': 'on',
                  'page_type_vocabulary': page_type})
    assert response.status_code == 302
    assert vocabulary_settings_and_cache.menu_management['vocabulary'] == {
        'show': True, 'page_type': page_type}


def test_vocabulary_admin_ui(authenticated_client):
    response = authenticated_client.get('/admin/sidebar-vocabulary-settings')
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'name="include_ids"' in html
    assert 'name="exclude_ids"' in html
    assert 'id="show_vocabulary"' in html
    assert 'id="default_vocabulary"' in html
    assert 'id="individual_vocabulary"' in html
    sidebar = html.split('id="admin-sidebar-nav"', 1)[1].split('</ul>', 1)[0]
    vocabulary_item = sidebar.split('href="#sidebar-vocabulary-settings"')[0]
    assert vocabulary_item.rsplit('<li', 1)[1].startswith(
        ' class="nav-item ms-3"')
    assert sidebar.index('href="#sidebar-content-group"') < sidebar.index(
        'href="#sidebar-vocabulary-settings"')
    assert 'aria-describedby="vocabulary-include-help"' in html


@pytest.mark.parametrize('page_type', ['default', 'individual'])
def test_vocabulary_individual_template(
        client, vocabulary_settings_and_cache, monkeypatch, tmp_path,
        page_type):
    templates = tmp_path / 'uploads' / 'templates'
    templates.mkdir(parents=True)
    (templates / 'vocabulary.html').write_text(
        '{% extends "layout.html" %}{% block content %}'
        '<p>Custom vocabulary {{ widget_language }}</p>{% endblock %}',
        encoding='utf-8')
    (tmp_path / 'application').mkdir()
    monkeypatch.setattr(app, 'root_path', str(tmp_path / 'application'))
    vocabulary_settings_and_cache.menu_management['vocabulary'][
        'page_type'] = page_type
    response = client.get('/vocabulary')
    assert response.status_code == 200
    assert (b'Custom vocabulary en' in response.data) == (
        page_type == 'individual')
    assert (b'<openatlas-vocabulary-viewer' in response.data) == (
        page_type == 'default')


def test_vocabulary_missing_individual_template_falls_back(
        client, vocabulary_settings_and_cache, monkeypatch, tmp_path):
    monkeypatch.setattr(app, 'root_path', str(tmp_path / 'application'))
    vocabulary_settings_and_cache.menu_management['vocabulary'][
        'page_type'] = 'individual'
    response = client.get('/vocabulary')
    assert response.status_code == 200
    assert b'<openatlas-vocabulary-viewer' in response.data


@pytest.mark.parametrize('language, expected', [
    ('de', 'de'), ('en', 'en'), ('hu', 'en')])
@pytest.mark.parametrize('filter_name', ['include', 'exclude', 'none'])
def test_vocabulary_page_attributes(
        client, vocabulary_settings_and_cache, language, expected,
        filter_name):
    settings = vocabulary_settings_and_cache
    if filter_name != 'none':
        setattr(settings, f'vocabulary_{filter_name}_ids', [42, 43])
    with client.session_transaction() as session:
        session['language'] = language
    response = client.get('/vocabulary')
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    widget = html.split('<openatlas-vocabulary-viewer', 1)[1].split('>', 1)[0]
    assert '<div class="container">' in html.split(
        'class="page-wrapper vocabulary-page', 1)[1].split(
        '<openatlas-vocabulary-viewer', 1)[0]
    assert f'lang="{expected}"' in widget
    assert 'tree-endpoint="/api/vocabulary/tree"' in widget
    assert 'detail-endpoint="/api/vocabulary/{id}"' in widget
    assert ('bootstrap-url="/static/node_modules/bootstrap/dist/css/'
            'bootstrap.min.css"') in widget
    assert ('type="module" src="/static/node_modules/'
            'openatlas-vocabulary-viewer/openatlas-vocabulary-viewer.js"') \
        in html
    for name in ('include', 'exclude'):
        assert (f'{name}-ids=' in widget) == (filter_name == name)
    if filter_name != 'none':
        assert f"{filter_name}-ids='[42, 43]'" in widget


@pytest.mark.parametrize('visible', [True, False])
def test_vocabulary_navbar_switch(
        client, vocabulary_settings_and_cache, visible):
    settings = vocabulary_settings_and_cache
    settings.menu_management['vocabulary']['show'] = visible
    response = client.get('/vocabulary')
    assert response.status_code == 200
    assert (b'href="/vocabulary"' in response.data) == visible
    assert b'<openatlas-vocabulary-viewer' in response.data


def test_vocabulary_page_global_restriction(
        client, vocabulary_settings_and_cache):
    vocabulary_settings_and_cache.access_restriction = True
    response = client.get('/vocabulary')
    assert response.status_code == 302
    assert response.location.endswith('/login')


@pytest.mark.parametrize('result, message', [
    (True, 'Vocabulary cache preload started in background.'),
    (False, 'Vocabulary cache preload is already running.'),
    (OSError('secret-path'), 'Could not start vocabulary cache preload.')])
def test_system_refresh_starts_vocabulary_background(
        authenticated_client, result, message):
    with patch('histarchexplorer.views.admin.start_vocabulary_refresh') \
            as start:
        if isinstance(result, Exception):
            start.side_effect = result
        else:
            start.return_value = result
        response = authenticated_client.get('/admin/refresh-system-cache')
    assert response.status_code == 302
    start.assert_called_once_with()
    with authenticated_client.session_transaction() as session:
        messages = [text for _, text in session['_flashes']]
    assert message in messages
    assert not any('secret-path' in text for text in messages)


def test_system_refresh_requires_manager(client):
    user = MagicMock(is_authenticated=True, group='user')
    with patch('flask_login.utils._get_user', return_value=user), \
            patch('histarchexplorer.views.admin.start_vocabulary_refresh') \
            as start:
        response = client.get('/admin/refresh-system-cache')
    assert response.status_code == 403
    start.assert_not_called()


def test_admin_displays_vocabulary_cache_status(authenticated_client):
    status = {
        'state': 'partial', 'total': 10, 'successful': 8, 'failed': 2,
        'started_at': '2026-10-08T12:00:00+00:00',
        'updated_at': '2026-10-08T12:10:00+00:00',
        'finished_at': '2026-10-08T12:10:00+00:00'}
    with patch('histarchexplorer.views.admin.get_vocabulary_cache_status',
               return_value=status):
        response = authenticated_client.get('/admin/sidebar-cache-options')
    assert response.status_code == 200
    assert b'Completed with errors' in response.data
    assert b'data-job-field="done">8</span>' in response.data
    assert b'data-job-field="total">10</span>' in response.data
    assert b'2026-10-08T12:10:00+00:00' in response.data


def test_global_cache_clear_removes_vocabulary_data(client):
    response = MagicMock()
    response.json.return_value = {'id': 42}
    with patch('histarchexplorer.api.api_access.requests.get',
               return_value=response) as fetch:
        for path in ('tree', '42'):
            assert client.get(f'/api/vocabulary/{path}').status_code == 200
            assert client.get(f'/api/vocabulary/{path}').status_code == 200
        assert fetch.call_count == 2
        cache.clear()
        for path in ('tree', '42'):
            assert client.get(f'/api/vocabulary/{path}').status_code == 200
        assert fetch.call_count == 4