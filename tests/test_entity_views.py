import pytest
from unittest.mock import patch, MagicMock
from flask.testing import FlaskClient
from histarchexplorer.api.presentation_view import PresentationView

@pytest.fixture
def mock_entity():
    pv = PresentationView(
        id=1, system_class="Site", view_class="site", title="Test Entity",
        description={"en": "Test"}, aliases=["T"], start="2023", end="2024"
    )
    # Mocking some more fields that views/entity.py expects
    pv.geometries = []
    pv.types = []
    pv.relations = {}
    pv.files = []
    pv.references = []
    return pv

from histarchexplorer.models.settings import Settings

def test_entity_view(authenticated_client: FlaskClient) -> None:
    with patch('histarchexplorer.api.presentation_view.PresentationView.from_api') as mock_from_api, \
         patch('histarchexplorer.models.settings.Settings.load_from_db') as mock_settings:
        
        # Use a real Settings object with defaults
        settings = Settings()
        settings.access_restriction = False
        mock_settings.return_value = settings
        
        pv = PresentationView(
            id=1, system_class="Site", view_class="site", title="Test Site",
            description={"en": "Test"}, aliases=[], start="2023", end="2024"
        )
        pv.geometries = []
        pv.types = []
        pv.relations = {}
        pv.files = []
        pv.references = []
        mock_from_api.return_value = pv
        
        rv = authenticated_client.get('/entity/1')
        assert rv.status_code == 200

def test_entities_view(authenticated_client: FlaskClient) -> None:
    with patch('histarchexplorer.database.entities.get_entities_list') as mock_get, \
         patch('histarchexplorer.models.settings.Settings.load_from_db') as mock_settings:
        
        settings = Settings()
        settings.access_restriction = False
        mock_settings.return_value = settings
        
        mock_get.return_value = [{"id": 1, "title": "E1", "openatlas_class_name": "site"}]
        rv = authenticated_client.get('/entities/site')
        assert rv.status_code == 200
        assert b'E1' in rv.data

from histarchexplorer.api.presentation_view import File, Relation, EntityTypeModel

def test_entity_view_tabs(authenticated_client: FlaskClient) -> None:
    with patch('histarchexplorer.api.presentation_view.PresentationView.from_api') as mock_from_api, \
         patch('histarchexplorer.models.settings.Settings.load_from_db') as mock_settings:
        
        settings = Settings()
        settings.access_restriction = False
        mock_settings.return_value = settings
        
        pv = PresentationView(
            id=1, system_class="feature", view_class="site", title="Test Feature",
            description={"en": "Test"}, aliases=[], start="2023", end="2024"
        )
        pv.geometries = []
        pv.types = []
        pv.relations = {'place': [
            Relation(id=2, name='P', system_class='place', geometries=[], geometry_json={})
        ]}
        pv.files = []
        pv.references = []
        mock_from_api.return_value = pv
        
        tabs = ['overview', 'map', 'media', 'subunits']
        for tab in tabs:
            rv = authenticated_client.get(f'/entity/1/{tab}')
            assert rv.status_code == 200

def test_get_entity_tabs(authenticated_client: FlaskClient) -> None:
    with patch('histarchexplorer.api.presentation_view.PresentationView.from_api') as mock_from_api, \
         patch('histarchexplorer.models.settings.Settings.load_from_db') as mock_settings, \
         patch('histarchexplorer.views.entity.get_browse_list_entities') as mock_sub:
        
        settings = Settings()
        settings.access_restriction = False
        mock_settings.return_value = settings
        mock_sub.return_value = {'counts': {}}
        
        tabs = ['overview', 'map', 'media', 'subunits']
        for tab in tabs:
            rv = authenticated_client.get(f'/get_entity/1/{tab}')
            assert rv.status_code == 200

def test_get_rastermaps(authenticated_client: FlaskClient) -> None:
    with patch('histarchexplorer.views.entity.get_files_for_ids') as mock_get:
        mock_get.return_value = {'images': []}
        rv = authenticated_client.post('/get_rastermaps', json={'ids': [1, 2]})
        assert rv.status_code == 200
