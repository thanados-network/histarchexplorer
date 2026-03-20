from flask.testing import FlaskClient


def test_admin_requires_login(client: FlaskClient) -> None:
    rv = client.get('/admin/')
    assert rv.status_code == 302


def test_admin_page(authenticated_client: FlaskClient) -> None:
    rv = authenticated_client.get('/admin/')
    assert rv.status_code == 200


def test_admin_tabs(authenticated_client: FlaskClient) -> None:
    tabs = ['general', 'team', 'projects', 'maps', 'assets', 'system']
    for tab in tabs:
        rv = authenticated_client.get(f'/admin/{tab}')
        assert rv.status_code == 200


def test_admin_update_menu_management(authenticated_client: FlaskClient) -> None:
    data = {
        'menu_data': '{"about": {"show": true, "page_type": "individual"}}'
    }
    rv = authenticated_client.post('/admin/update_menu_management', data=data)
    assert rv.status_code == 302


def test_admin_update_legal_notice(authenticated_client: FlaskClient) -> None:
    data = {
        'legal_notice_de': 'Test DE',
        'legal_notice_en': 'Test EN'
    }
    rv = authenticated_client.post('/admin/update_legal_notice', data=data)
    assert rv.status_code == 302


def test_admin_add_available_color(authenticated_client: FlaskClient) -> None:
    data = {'new_color': '#ff0000'}
    rv = authenticated_client.post('/admin/add_available_color', data=data)
    assert rv.status_code == 302


def test_admin_delete_available_color(authenticated_client: FlaskClient) -> None:
    data = {'color_to_delete': '#ff0000'}
    rv = authenticated_client.post('/admin/delete_available_color', data=data)
    assert rv.status_code == 302


def test_admin_update_class_visibility(authenticated_client: FlaskClient) -> None:
    data = {'visibility_data': '{"place": true}'}
    rv = authenticated_client.post('/admin/update_class_visibility', data=data)
    assert rv.status_code == 302


def test_admin_clear_cache(authenticated_client: FlaskClient) -> None:
    rv = authenticated_client.get('/admin/clear-cache')
    assert rv.status_code == 302


def test_admin_refresh_system_cache(authenticated_client: FlaskClient) -> None:
    rv = authenticated_client.get('/admin/refresh-system-cache')
    assert rv.status_code == 302


def test_admin_backup_db(authenticated_client: FlaskClient) -> None:
    # This might fail if pg_dump is not available or if it tries to write to a protected dir
    # But it should at least return a response
    rv = authenticated_client.get('/admin/backup_db')
    assert rv.status_code in (200, 302)


def test_admin_add_license(authenticated_client: FlaskClient) -> None:
    data = {
        'license_name': 'Test License',
        'license_url': 'http://example.com',
        'spdx_id': 'Test-1.0',
        'uri': 'http://example.com/uri',
        'category': 'LICENSE',
        'label': 'Test Label'
    }
    rv = authenticated_client.post('/admin/add_license', data=data)
    assert rv.status_code == 302
