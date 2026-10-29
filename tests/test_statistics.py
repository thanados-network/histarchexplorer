from unittest.mock import MagicMock, patch

from flask import g
from flask.testing import FlaskClient

from histarchexplorer import cache
from histarchexplorer.models.settings import Settings
from histarchexplorer.services.statistics import (
    CLASS_KPI_META, build_dynamic_landing_sections,
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
        cache.delete_memoized(get_landing_statistics)
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

        executed_queries = [
            call.args[0] for call in mock_cursor.execute.call_args_list]
        assert "h.category = 'standard'" in executed_queries[1]
        assert "h.category = 'standard'" in executed_queries[2]


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
        cache.delete_memoized(get_landing_sites_geojson)
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            {
                'id': 48267,
                'name': 'Mitterretzbach',
                'lng': 15.98,
                'lat': 48.77,
                'begin': '000000600-01-01',
                'end': '000000749-01-01'},
            {
                'id': 2,
                'name': 'Reichertshausen',
                'lng': 11.50,
                'lat': 48.46,
                'begin': '000000779-02-20',
                'end': None},
            {
                'id': 3,
                'name': 'Prehistoric Site',
                'lng': 16.37,
                'lat': 48.20,
                'begin': '-000000800-01-01',
                'end': '-000000500-12-31'}]
        g.openatlas_cursor = mock_cursor

        geo = get_landing_sites_geojson((999,))
        assert geo['type'] == 'FeatureCollection'
        assert len(geo['features']) == 3
        feat0 = geo['features'][0]
        assert feat0['properties']['name'] == 'Mitterretzbach'
        assert feat0['properties']['dating'] == '600 – 749'
        assert feat0['geometry']['coordinates'] == [15.98, 48.77]

        feat1 = geo['features'][1]
        assert feat1['properties']['dating'] == '20.02.779'

        feat2 = geo['features'][2]
        assert feat2['properties']['dating'] == '800 BC – 500 BC'

        executed_sql = mock_cursor.execute.call_args.args[0]
        executed_params = mock_cursor.execute.call_args.args[1]
        assert 'tng.getdates' not in executed_sql
        assert executed_sql % executed_params


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
    assert 'Open Interfaces & Standards' not in html
    assert 'heroSearchDropdown' in html
    assert (
        'window.landingMapStyle = '
        '"https://api.maptiler.com/maps/bright/style.json'
        '?key=E7Jrgaazm79UlTuEI5f5";') in html


def test_build_dynamic_landing_sections_respects_shown_and_predefined_filters(
        app_instance) -> None:
    """Verify dynamic KPI cards and predefined filter thematic cards."""
    with app_instance.test_request_context('/'):
        g.settings = Settings(
            shown_classes=['place', 'person', 'event', 'artifact', 'file'],
            hidden_classes=['artifact'])
        g.view_classes = app_instance.config['VIEW_CLASSES']
        g.language = 'en'
        g.predefined_filters = [
            {
                'id': 1,
                'label': 'Thanados',
                'description': 'Show only Thanados entities.',
                'icon': None,
                'tabs': ['places', 'features', 'items'],
                'filter_parameters': {'classes': ['place', 'artifact']}},
            {
                'id': 2,
                'label': {'en': 'Churches before 1300'},
                'description': {'en': 'Medieval churches'},
                'icon': {'type': 'css', 'value': 'bi-building'},
                'tabs': ['places'],
                'filter_parameters': {'type_ids': [285]}}]

        landing_stats = {
            'class_counts': {
                'place': 12,
                'person': 7,
                'event': 3,
                'artifact': 99,
                'file': 0}}
        kpi_cards, thematic_cards = build_dynamic_landing_sections(
            landing_stats, {})

        kpi_classes = [c['class_name'] for c in kpi_cards]
        assert kpi_classes == ['place', 'person', 'event']
        assert 'artifact' not in kpi_classes
        assert 'file' not in kpi_classes

        assert len(thematic_cards) == 2
        assert thematic_cards[0]['id'] == 1
        assert thematic_cards[0]['title'] == 'Thanados'
        assert thematic_cards[0]['target_tab'] == 'places'
        assert [b['tab'] for b in thematic_cards[0]['tab_buttons']] == [
            'places', 'features', 'items']
        assert thematic_cards[0]['icon_type'] == 'img'
        assert thematic_cards[0]['icon_value'].endswith('place.png')

        assert thematic_cards[1]['id'] == 2
        assert thematic_cards[1]['title'] == 'Churches before 1300'
        assert thematic_cards[1]['icon_type'] == 'css'
        assert thematic_cards[1]['icon_value'] == 'bi bi-building'

        for classes in app_instance.config['VIEW_CLASSES'].values():
            for cls in classes:
                assert cls in CLASS_KPI_META
                assert CLASS_KPI_META[cls]['icon'].startswith('bi-')


def test_search_live_all_endpoint(
        authenticated_client: FlaskClient) -> None:
    """Verify /search_live queries /api/1/search and normalizes results."""
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            'data': [{
                'id': 119152,
                'uuid': 'd77945ed-537e-476c-a716-df523982a162',
                'name': 'Thunau Burial Mounds',
                'description': 'Early medieval burial mounds.',
                'systemClass': 'place',
                'timespan': None}],
            'totalItems': 1,
            'first': 'https://thanados.openatlas.eu/api/1/search?page=1',
            'last': 'https://thanados.openatlas.eu/api/1/search?page=1'}
        rv = authenticated_client.get('/search_live?search=Thunau')
        assert rv.status_code == 200
        data = rv.get_json()
        assert len(data) == 1
        assert data[0]['id'] == '119152'
        assert data[0]['name'] == 'Thunau Burial Mounds'
        assert data[0]['systemClass'] == 'place'
        assert data[0]['system_class'] == 'place'
        called_url = mock_get.call_args.args[0]
        called_params = mock_get.call_args.kwargs['params']
        assert called_url.endswith('/1/search')
        assert called_params['search'] == 'Thunau'
        assert 'entityClass' not in called_params
