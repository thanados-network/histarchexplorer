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
        pv = PresentationView(
            id=1, system_class="feature", view_class="feature",
            title="Test Feature", description={"en": "Test"},
            aliases=[], start="2023", end="2024"
        )
        pv.geometries = []
        pv.types = []
        pv.relations = {
            'stratigraphic_unit': [
                Relation(
                    id=10,
                    name='SU 10',
                    system_class='stratigraphic_unit',
                    description={'en': 'Primary burial cut'},
                    aliases=['SU-X'],
                    relation_types=[{
                        'relationTo': 1,
                        'property': 'crm:P46i_forms_part_of'}],
                    types=[
                        EntityTypeModel(
                            id=101,
                            title='Grave fill',
                            descriptions=None,
                            is_standard=True,
                            type_hierarchy=None,
                            value=None,
                            unit=None,
                            division=None)],
                    geometries=[],
                    geometry_json={})],
            'artifact': [
                Relation(
                    id=20,
                    name='Artifact A',
                    system_class='artifact',
                    description={'en': 'Bronze brooch with spiral motif'},
                    aliases=['A-20'],
                    relation_types=[{
                        'relationTo': 10,
                        'property': 'crm:P46i_forms_part_of'}],
                    types=[
                        EntityTypeModel(
                            id=102,
                            title='Brooch',
                            descriptions=None,
                            is_standard=True,
                            type_hierarchy=None,
                            value=None,
                            unit=None,
                            division=None)],
                    geometries=[],
                    geometry_json={})],
            'human_remains': [
                Relation(
                    id=30,
                    name='Remains R',
                    system_class='human_remains',
                    description={'en': 'Adult individual, supine position'},
                    aliases=['HR-30'],
                    relation_types=[{
                        'relationTo': 10,
                        'property': 'crm:P46i_forms_part_of'}],
                    types=[
                        EntityTypeModel(
                            id=103,
                            title='Inhumation',
                            descriptions=None,
                            is_standard=True,
                            type_hierarchy=None,
                            value=None,
                            unit=None,
                            division=None)],
                    geometries=[],
                    geometry_json={})]}
        pv.files = []
        pv.references = []
        pv.geometry_json = {}
        mock_from_api.return_value = pv

        tabs = ['overview', 'map', 'media', 'subunits', 'feature']
        for tab in tabs:
            rv = authenticated_client.get(f'/get_entity/1/{tab}')
            assert rv.status_code == 200
            if tab == 'feature':
                assert b'Stratigraphic Overview' in rv.data
                assert b'SU 10' in rv.data
                assert b'Artifact A' in rv.data
                assert b'Remains R' in rv.data
                assert b'Artifact Details' in rv.data
                assert b'Human Remains Details' in rv.data
                assert b'Bronze brooch with spiral motif' in rv.data
                assert b'Adult individual, supine position' in rv.data
                assert b'thanados.openatlas.eu/api/query/' not in rv.data

def test_get_rastermaps(authenticated_client: FlaskClient) -> None:
    with patch('histarchexplorer.views.entity.get_files_for_ids') as mock_get:
        mock_get.return_value = {'images': []}
        rv = authenticated_client.post('/get_rastermaps', json={'ids': [1, 2]})
        assert rv.status_code == 200
