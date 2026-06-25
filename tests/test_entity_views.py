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

def _part_of(parent_id):
    return [{
        'relationTo': parent_id,
        'property': 'crm:P46i_forms_part_of'}]


def _build_sub_view(id_, system_class, title, description, types=None,
                    files=None):
    pv = PresentationView(
        id=id_, system_class=system_class, view_class=system_class,
        title=title, description={'en': description}, aliases=[],
        start=None, end=None)
    pv.geometries = []
    pv.geometry_json = {}
    pv.types = types or []
    pv.relations = {}
    pv.files = files or []
    pv.references = []
    return pv


def test_get_entity_tabs(authenticated_client: FlaskClient) -> None:
    from histarchexplorer.api.presentation_view import (
        TimePointModel, TimeRangeModel)
    with patch('histarchexplorer.api.presentation_view.PresentationView.from_api') as mock_from_api, \
         patch('histarchexplorer.models.settings.Settings.load_from_db') as mock_settings, \
         patch('histarchexplorer.views.entity.get_browse_list_entities') as mock_sub:

        settings = Settings()
        settings.access_restriction = False
        mock_settings.return_value = settings
        mock_sub.return_value = {'counts': {}}

        # Clicked feature with two stratigraphic units and finds linked
        # to each unit.
        feature = PresentationView(
            id=1, system_class="feature", view_class="feature",
            title="Test Feature", description={"en": "Feature description"},
            aliases=[], start=None, end=None)
        feature.geometries = []
        feature.geometry_json = {}
        feature_main_type = EntityTypeModel(
            id=200, title='Grave', descriptions={'en': 'A grave'},
            is_standard=True, type_hierarchy=[], value=None, unit=None,
            division=None)
        feature.types = [feature_main_type]
        feature.files = []
        feature.references = []
        feature.relations = {
            'stratigraphic_unit': [
                Relation(
                    id=10, name='SU 10', system_class='stratigraphic_unit',
                    relation_types=_part_of(1)),
                Relation(
                    id=11, name='SU 11', system_class='stratigraphic_unit',
                    relation_types=_part_of(1))],
            'artifact': [
                Relation(
                    id=20, name='Artifact A', system_class='artifact',
                    relation_types=_part_of(10)),
                Relation(
                    id=21, name='Artifact B', system_class='artifact',
                    relation_types=_part_of(11))],
            'human_remains': [
                Relation(
                    id=30, name='Remains R', system_class='human_remains',
                    relation_types=_part_of(10))]}

        su10_type = EntityTypeModel(
            id=101, title='Grave fill', descriptions={'en': 'Fill type'},
            is_standard=False, type_hierarchy=[], value=None, unit=None,
            division={'label': 'case study'})
        su10 = _build_sub_view(
            10, 'stratigraphic_unit', 'SU 10', 'Primary burial cut',
            types=[su10_type])
        su10.when = TimeRangeModel(
            start=TimePointModel(earliest='-0050-01-01T00:00:00'),
            end=TimePointModel(latest='0120-12-31T00:00:00'))
        su11 = _build_sub_view(
            11, 'stratigraphic_unit', 'SU 11', 'Secondary deposit')

        valid_image = File(
            id=901, title='img', license='CC', public=True,
            url='https://example.org/valid.jpg', mime_type='image/jpeg',
            iiif_base_path='https://iiif.example.org/901',
            from_super_entity=False, render_type='image')
        super_image = File(
            id=902, title='inherited', license='CC', public=True,
            url='https://example.org/inherited.jpg', mime_type='image/jpeg',
            iiif_base_path='https://iiif.example.org/902',
            from_super_entity=True, render_type='image')
        artifact_a = _build_sub_view(
            20, 'artifact', 'Artifact A', 'Bronze brooch with spiral motif',
            files=[valid_image, super_image])
        artifact_b = _build_sub_view(
            21, 'artifact', 'Artifact B', 'Iron nail fragment')
        remains_r = _build_sub_view(
            30, 'human_remains', 'Remains R',
            'Adult individual, supine position')

        views = {
            1: feature, 10: su10, 11: su11,
            20: artifact_a, 21: artifact_b, 30: remains_r}
        mock_from_api.side_effect = lambda id_: views[id_]

        tabs = ['overview', 'map', 'media', 'subunits', 'feature']
        for tab in tabs:
            rv = authenticated_client.get(f'/get_entity/1/{tab}')
            assert rv.status_code == 200
            if tab == 'feature':
                body = rv.data.decode('utf-8')
                # All entities rendered.
                for title in ['Test Feature', 'SU 10', 'SU 11',
                              'Artifact A', 'Artifact B', 'Remains R']:
                    assert title in body
                # Descriptions rendered.
                assert 'Bronze brooch with spiral motif' in body
                assert 'Adult individual, supine position' in body
                # Sequential grouping: SU 10 + its finds before SU 11.
                assert (body.index('SU 10') < body.index('Artifact A')
                        < body.index('SU 11'))
                assert body.index('Remains R') < body.index('SU 11')
                # Artifact B belongs to SU 11 and comes after it.
                assert body.index('SU 11') < body.index('Artifact B')
                # Type badge with clickable popover.
                assert 'data-bs-toggle="popover"' in body
                # Main (standard) type rendered as a badge next to title.
                assert 'Grave' in body
                # Compact year span (earliest begin .. latest end).
                assert '50 BC' in body
                assert '120 AD' in body
                # No dummy placeholder image.
                assert 'dummyimage.com' not in body
                # Inherited image excluded, valid image present.
                assert 'iiif.example.org/901' in body
                assert 'iiif.example.org/902' not in body

def test_get_rastermaps(authenticated_client: FlaskClient) -> None:
    with patch('histarchexplorer.views.entity.get_files_for_ids') as mock_get:
        mock_get.return_value = {'images': []}
        rv = authenticated_client.post('/get_rastermaps', json={'ids': [1, 2]})
        assert rv.status_code == 200
