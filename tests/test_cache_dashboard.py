"""Admin cache dashboard and its JSON status endpoint."""

from unittest.mock import patch


def test_dashboard_and_status_endpoint(authenticated_client):
    response = authenticated_client.get('/admin/cache-status')
    assert response.status_code == 200
    assert {'entities', 'vocabulary'} <= set(response.get_json())
    page = authenticated_client.get('/admin/sidebar-cache-options')
    assert page.status_code == 200
    html = page.get_data(as_text=True)
    assert 'cacheDashboard' in html
    assert 'refreshStaleEntities' in html


def test_stale_route_starts_stale_mode(authenticated_client):
    with patch('histarchexplorer.views.admin.start_entity_warmup',
               return_value=True) as start:
        response = authenticated_client.get('/admin/refresh-stale-entities')
    assert response.status_code == 302
    assert start.call_args.args[0] == 'stale'
