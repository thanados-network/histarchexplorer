"""Contract and characterization tests for entities browsing views.

Phase 0 safety net to ensure refactoring does not break existing data
structures, return formats, or UI routing behavior.
"""

from collections.abc import Generator
from contextlib import contextmanager
from unittest.mock import MagicMock, patch

import pytest
from flask.testing import FlaskClient

from histarchexplorer import app
from histarchexplorer.models.settings import Settings
from histarchexplorer.views.entities import (
    get_browse_list_entities,
    get_browse_metadata,
    get_browse_tab_data)


@pytest.fixture(autouse=True)
def standard_settings_fixture() -> Generator[None, None, None]:
    """Ensure tests run against standard settings without test bleed."""
    default_settings = Settings()
    with patch(
        'histarchexplorer.models.settings.Settings.load_from_db',
        return_value=default_settings
    ):
        yield


@contextmanager
def auth_request_context(
        path: str = '/entities') -> Generator[None, None, None]:
    """Provide a request context with an authenticated admin user."""
    mock_user = MagicMock()
    mock_user.is_authenticated = True
    default_settings = Settings()
    with patch(
        'flask_login.utils._get_user', return_value=mock_user
    ), patch(
        'histarchexplorer.views.login.load_user', return_value=mock_user
    ), patch(
        'histarchexplorer.models.settings.Settings.load_from_db',
        return_value=default_settings
    ):
        with app.test_request_context(path):
            app.preprocess_request()
            yield


def test_get_browse_list_entities_contract_keys() -> None:
    """Verify that get_browse_list_entities(0) provides all expected keys."""
    with auth_request_context('/entities'):
        data = get_browse_list_entities(0)

        assert isinstance(data, dict)
        expected_keys = {
            'shown classes', 'hidden classes', 'shown types', 'hidden types',
            'shown case studies', 'shown ids', 'hidden ids', 'entities',
            'geometries', 'cs_ids', 'totals', 'counts'}
        assert expected_keys.issubset(set(data.keys()))


def test_get_browse_list_entities_contract_types() -> None:
    """Verify internal value types and shapes in browse list data."""
    with auth_request_context('/entities'):
        data = get_browse_list_entities(0)
        assert data is not None

        assert isinstance(data['totals'], dict)
        assert isinstance(data['counts'], dict)
        assert isinstance(data['cs_ids'], list)

        for category, total in data['totals'].items():
            assert isinstance(total, int)
            assert total >= 0

        for category, count_list in data['counts'].items():
            assert isinstance(count_list, list)
            category_sum = 0
            for item in count_list:
                assert isinstance(item, dict)
                for class_name, count in item.items():
                    assert isinstance(class_name, str)
                    assert isinstance(count, int)
                    category_sum += count
            assert category_sum == data['totals'].get(category, 0)

        if data.get('entities'):
            entity = data['entities'][0]
            assert isinstance(entity, dict)
            for req_field in ('id', 'name', 'class'):
                assert req_field in entity
            assert isinstance(entity['id'], int)

        geoms = data.get('geometries')
        if isinstance(geoms, dict):
            assert geoms.get('type') == 'FeatureCollection'
            features = geoms.get('features')
            assert features is None or isinstance(features, list)
            if features:
                feature = features[0]
                assert feature.get('type') == 'Feature'
                assert 'properties' in feature
                assert 'geometry' in feature


def test_get_browse_list_entities_nonexistent_returns_none() -> None:
    """Verify that querying children for an invalid entity ID yields None."""
    with auth_request_context('/entities'):
        data = get_browse_list_entities(999999999)
        assert data is None


def test_get_browse_list_entities_subunits_parent() -> None:
    """Verify contract when querying valid child entities via parent ID."""
    with auth_request_context('/entities'):
        # Entity 45143 has valid children in the test database
        data = get_browse_list_entities(45143)
        if data is not None:
            assert isinstance(data, dict)
            assert 'totals' in data
            assert 'counts' in data
            assert 'entities' in data


def test_entities_endpoint_html_structure(
        authenticated_client: FlaskClient) -> None:
    """Verify the response contract and HTML shell for /entities."""
    rv = authenticated_client.get('/entities')
    assert rv.status_code == 200
    assert 'text/html' in rv.content_type

    html = rv.data.decode('utf-8')
    assert '<title>Histarchexplorer</title>' in html
    assert 'id="nav-sidebar"' in html
    assert 'tab-pane-' in html


def test_entities_tab_route_contract(
        authenticated_client: FlaskClient) -> None:
    """Verify that passing tab_name to /entities route succeeds."""
    rv = authenticated_client.get('/entities/places')
    assert rv.status_code == 200
    assert 'text/html' in rv.content_type


def test_get_entities_partial_template(
        authenticated_client: FlaskClient) -> None:
    """Verify /get_entities/<tab_name> returns partial browse layout."""
    rv = authenticated_client.get('/get_entities/places')
    assert rv.status_code == 200
    assert 'text/html' in rv.content_type

    html = rv.data.decode('utf-8')
    assert 'table-places' in html
    assert 'browse-header' in html


def test_baseline_metrics_recorded(
        authenticated_client: FlaskClient) -> None:
    """Verify that Phase 2 reduced /entities initial payload to < 50 KB."""
    rv = authenticated_client.get('/entities')
    assert rv.status_code == 200
    payload_size = len(rv.data)
    # Baseline was ~26.7 MB. Phase 2 decouples data and reduces to < 50 KB.
    assert payload_size < 50_000
    assert payload_size > 10_000


def test_get_browse_metadata_contract() -> None:
    """Verify return structure and keys of get_browse_metadata."""
    with auth_request_context('/entities'):
        meta = get_browse_metadata(0)
        assert meta is not None
        assert isinstance(meta, dict)
        for key in ('totals', 'counts', 'cs_ids', 'shown classes'):
            assert key in meta
        # Should NOT contain full entities or geometries
        assert 'entities' not in meta
        assert 'geometries' not in meta


def test_get_browse_tab_data_places() -> None:
    """Verify get_browse_tab_data returns scoped entities and geometries."""
    with auth_request_context('/entities'):
        tab_data = get_browse_tab_data('places')
        assert isinstance(tab_data, dict)
        assert 'entities' in tab_data
        assert 'geometries' in tab_data
        assert len(tab_data['entities']) > 0
        # All entities must belong to places classes
        for ent in tab_data['entities']:
            assert ent['class'] in ('place', 'feature', 'stratigraphic_unit')


def test_phase1_lazy_loading_and_model_viewer_isolation(
        authenticated_client: FlaskClient) -> None:
    """Verify lazy tab loading marker and model-viewer script isolation."""
    rv = authenticated_client.get('/entities')
    assert rv.status_code == 200
    html = rv.data.decode('utf-8')
    assert 'const initialActiveTab =' in html
    assert 'model-viewer-umd.js' not in html

    rv_viewer = authenticated_client.get('/view/3d_model/1')
    assert rv_viewer.status_code == 200
    viewer_html = rv_viewer.data.decode('utf-8')
    assert 'model-viewer-umd.js' in viewer_html


def test_phase1_map_on_demand_initialization(
        authenticated_client: FlaskClient) -> None:
    """Verify on-demand MapLibre initialization in partial templates."""
    rv_places = authenticated_client.get('/get_entities/places')
    assert rv_places.status_code == 200
    places_html = rv_places.data.decode('utf-8')
    assert 'function initMapplaces()' in places_html
    assert 'let mapplaces = null;' in places_html

    rv_items = authenticated_client.get('/get_entities/items')
    assert rv_items.status_code == 200
    items_html = rv_items.data.decode('utf-8')
    assert 'function initMapitems()' in items_html
    assert 'let mapitems = null;' in items_html


def test_get_browse_tab_data_without_geometries() -> None:
    """Verify include_geometries=False returns empty FeatureCollection."""
    with auth_request_context('/entities'):
        tab_data = get_browse_tab_data('places', include_geometries=False)
        assert isinstance(tab_data, dict)
        assert 'geometries' in tab_data
        assert tab_data['geometries']['type'] == 'FeatureCollection'
        assert tab_data['geometries']['features'] == []
        assert len(tab_data['entities']) > 0


def test_api_browse_geometries_places_contract(
        authenticated_client: FlaskClient) -> None:
    """Verify places geometries endpoint returns GeoJSON FeatureCollection."""
    rv = authenticated_client.get('/api/browse/places/geometries')
    assert rv.status_code == 200
    assert 'application/json' in rv.content_type
    data = rv.get_json()
    assert isinstance(data, dict)
    assert data.get('type') == 'FeatureCollection'
    features = data.get('features')
    assert isinstance(features, list)
    assert len(features) > 0
    feature = features[0]
    assert feature.get('type') == 'Feature'
    assert 'geometry' in feature
    assert 'properties' in feature
    assert feature['properties']['class'] in (
        'place', 'feature', 'stratigraphic_unit')


def test_api_browse_geometries_items_contract(
        authenticated_client: FlaskClient) -> None:
    """Verify items geometries endpoint returns GeoJSON FeatureCollection."""
    rv = authenticated_client.get('/api/browse/items/geometries')
    assert rv.status_code == 200
    assert 'application/json' in rv.content_type
    data = rv.get_json()
    assert isinstance(data, dict)
    assert data.get('type') == 'FeatureCollection'
    assert isinstance(data.get('features'), list)


def test_api_browse_geometries_invalid_tab_returns_404(
        authenticated_client: FlaskClient) -> None:
    """Verify non-map tabs return 404 for geometries API."""
    rv = authenticated_client.get('/api/browse/actors/geometries')
    assert rv.status_code == 404


def test_get_entities_places_payload_reduced(
        authenticated_client: FlaskClient) -> None:
    """Verify /get_entities/places omits geometries reducing payload size."""
    rv = authenticated_client.get('/get_entities/places')
    assert rv.status_code == 200
    html = rv.data.decode('utf-8')
    assert 'loadGeometriesplaces' in html
    assert '/api/browse/places/geometries' in html
    assert '"geometries": {"features": [], "type": "FeatureCollection"}' in (
        html)

