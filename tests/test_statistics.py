from unittest.mock import MagicMock

from flask import g
from flask.testing import FlaskClient

from histarchexplorer.services.statistics import (
    get_landing_sites_geojson, get_landing_statistics)


def test_get_landing_statistics_empty(
        app_instance) -> None:
    """Test fallback when no case study IDs are provided."""
    with app_instance.app_context():
        stats = get_landing_statistics(())
        assert 'chronology' in stats
        assert 'site_types' in stats
        assert 'artifact_types' in stats
        assert 'kpis' in stats
        assert stats['kpis']['places'] == 0


def test_get_landing_statistics_mocked(
        app_instance) -> None:
    """Test landing statistics calculation with mocked openatlas cursor."""
    with app_instance.test_request_context('/'):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.side_effect = [
            [{'century': 600, 'count': 42}],
            [{'name': 'Church', 'count': 10}],
            [{'name': 'vessel', 'count': 15}],
            [{'openatlas_class_name': 'place', 'count': 100},
             {'openatlas_class_name': 'feature', 'count': 250}]]
        g.openatlas_cursor = mock_cursor

        stats = get_landing_statistics((123,))
        assert len(stats['chronology']) == 1
        assert stats['chronology'][0]['century'] == '600 CE'
        assert len(stats['site_types']) == 1
        assert len(stats['artifact_types']) == 1
        assert stats['kpis']['places'] == 100
        assert stats['kpis']['features'] == 250


def test_get_landing_sites_geojson_empty(
        app_instance) -> None:
    """Test empty GeoJSON fallback."""
    with app_instance.app_context():
        geo = get_landing_sites_geojson(())
        assert geo['type'] == 'FeatureCollection'
        assert geo['features'] == []


def test_get_landing_sites_geojson_mocked(
        app_instance) -> None:
    """Test GeoJSON generation with mocked rows."""
    with app_instance.test_request_context('/'):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [{
            'id': 1,
            'name': 'Test Site',
            'lng': 16.37,
            'lat': 48.20,
            'begin': '0500-01-01',
            'end': '0600-12-31'}]
        g.openatlas_cursor = mock_cursor

        geo = get_landing_sites_geojson((999,))
        assert geo['type'] == 'FeatureCollection'
        assert len(geo['features']) == 1
        feat = geo['features'][0]
        assert feat['properties']['name'] == 'Test Site'
        assert feat['geometry']['coordinates'] == [16.37, 48.2]


def test_landing_sites_geojson_endpoint(
        authenticated_client: FlaskClient) -> None:
    """Test API endpoint /api/landing/sites-geojson."""
    rv = authenticated_client.get('/api/landing/sites-geojson')
    assert rv.status_code == 200
    data = rv.get_json()
    assert data['type'] == 'FeatureCollection'


def test_index_page_contains_no_lorem_ipsum(
        authenticated_client: FlaskClient) -> None:
    """Verify modern index page renders without any dummy placeholder text."""
    rv = authenticated_client.get('/')
    assert rv.status_code == 200
    html = rv.data.decode('utf-8')
    assert 'Lorem ipsum' not in html
    assert 'hero-section' in html
    assert 'landingStats' in html
