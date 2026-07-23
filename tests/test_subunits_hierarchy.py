from unittest.mock import MagicMock, patch

from flask import g
from flask.testing import FlaskClient

from histarchexplorer import app
from histarchexplorer.views.entity import (
    get_catalogue_data, get_map_sidebar_data, get_subunits_root_id,
    normalize_subunits_data)


def test_normalize_subunits_data_preserves_card_hierarchy():
    payload = {
        'features': [{
            'id': 1,
            'title': 'Feature',
            'systemClass': 'feature',
            'description': {'en': 'Feature description'},
            'when': {
                'start': {'earliest': '-0500-01-01'},
                'end': {'latest': '0100-12-31'}},
            'types': [{
                'id': 10,
                'title': 'Standard',
                'isStandard': True,
                'typeHierarchy': []}],
            'subunits': [{
                'id': 2,
                'title': 'First unit',
                'systemClass': 'stratigraphic_unit',
                'types': [{
                    'id': 11,
                    'title': 'Grave',
                    'isStandard': False,
                    'typeHierarchy': []}],
                'children': [{
                    'id': 3,
                    'title': 'Artifact',
                    'systemClass': 'artifact',
                    'files': [{
                        'id': 4,
                        'title': 'Own image',
                        'mimetype': 'image/jpeg',
                        'license': 'CC-BY',
                        'publicShareable': True,
                        'url': 'https://example.org/image.jpg',
                        'mainImage': True,
                        'fromSuperEntity': False}, {
                        'id': 5,
                        'title': 'Inherited image',
                        'mimetype': 'image/jpeg',
                        'license': 'CC-BY',
                        'publicShareable': True,
                        'url': 'https://example.org/inherited.jpg',
                        'fromSuperEntity': True}]}]}, {
                'id': 6,
                'title': 'Second unit',
                'systemClass': 'stratigraphic_unit',
                'children': [{
                    'id': 7,
                    'title': 'Human remains',
                    'systemClass': 'human_remains'}]}]}]}
    with app.test_request_context():
        g.type_divisions = {}
        hierarchy = normalize_subunits_data(payload)

    assert [group['su']['id'] for group in hierarchy[0]['groups']] == [2, 6]
    feature = hierarchy[0]['feature']
    assert feature['year_span'] == '500 BC – 100 AD'
    assert feature['description'] == {'en': 'Feature description'}
    assert feature['main_types'][0].title == 'Standard'
    artifact = hierarchy[0]['groups'][0]['children'][0]
    assert artifact['images'][0].id == 4
    assert hierarchy[0]['groups'][1]['children'][0]['id'] == 7


def test_normalize_subunits_data_skips_malformed_entries():
    with app.test_request_context():
        g.type_divisions = {}
        assert normalize_subunits_data({
            'features': [{'id': 'not-an-int', 'systemClass': 'feature'}]}) == []


def test_normalize_subunits_data_adapts_flat_graph_response():
    payload = {'50505': [{
        'id': 50505,
        'openatlasClassName': 'place',
        'children': [56623]}, {
        'id': 56623,
        'openatlasClassName': 'feature',
        'children': [56624],
        'properties': {
            'name': 'Feature title',
            'files': [{
                'id': 11,
                'name': 'Feature image',
                'mimetype': 'image/bmp',
                'url': 'https://example.org/image.bmp',
                'IIIFBasePath': 'https://images.example.org/11.bmp'}],
            'timespan': {
                'earliestBegin': '-0500-01-01',
                'latestEnd': '0100-12-31'},
            'standardType': {
                'id': 10,
                'name': 'Grave',
                'typeHierarchy': []}}}, {
        'id': 56624,
        'openatlasClassName': 'stratigraphic_unit',
        'children': [56625],
        'properties': {'name': 'Unit'}}, {
        'id': 56625,
        'openatlasClassName': 'artifact',
        'children': [],
        'properties': {'name': 'Artifact'}}]}
    with app.test_request_context():
        g.type_divisions = {}
        hierarchy = normalize_subunits_data(payload)

    assert hierarchy[0]['feature']['id'] == 56623
    assert hierarchy[0]['feature']['year_span'] == '500 BC – 100 AD'
    assert hierarchy[0]['feature']['main_types'][0].title == 'Grave'
    assert hierarchy[0]['feature']['images'][0].title == 'Feature image'
    assert hierarchy[0]['feature']['images'][0].iiif_base_path == (
        'https://images.example.org/11.bmp')
    assert hierarchy[0]['groups'][0]['su']['id'] == 56624
    assert hierarchy[0]['groups'][0]['children'][0]['id'] == 56625


def test_get_subunits_root_id_uses_containing_place():
    root = MagicMock(id=50505)
    with patch('histarchexplorer.views.entity.PresentationView.from_api'), \
            patch('histarchexplorer.views.entity.get_hierarchy',
                  return_value=[root]):
        assert get_subunits_root_id(56939) == 50505


def test_get_subunits_root_id_keeps_place_id():
    with patch('histarchexplorer.views.entity.PresentationView.from_api'), \
            patch('histarchexplorer.views.entity.get_hierarchy',
                  return_value=[]):
        assert get_subunits_root_id(50505) == 50505


def test_hierarchy_data_uses_containing_place_subunits():
    payload = {'features': [{
        'id': 1,
        'title': 'Feature',
        'systemClass': 'feature',
        'subunits': []}, {
        'id': 2,
        'title': 'Other feature',
        'systemClass': 'feature',
        'subunits': []}]}
    with app.test_request_context(), patch(
            'histarchexplorer.views.entity.ApiAccess.get_subunits',
            return_value=payload) as get_subunits, patch(
            'histarchexplorer.views.entity.get_subunits_root_id',
            return_value=50505) as get_root_id:
        g.type_divisions = {}
        assert get_map_sidebar_data(2)['feature']['title'] == 'Other feature'
        assert len(get_catalogue_data(1)) == 2

    assert get_root_id.call_args_list[0].args == (2,)
    assert get_root_id.call_args_list[1].args == (1,)
    assert get_subunits.call_args_list[0].args == (50505,)
    assert get_subunits.call_args_list[1].args == (50505,)


def test_hierarchy_routes_render_from_subunits(
        authenticated_client: FlaskClient):
    payload = {'features': [{
        'id': 1,
        'title': 'Feature title',
        'systemClass': 'feature',
        'files': [{
            'id': 11,
            'title': 'Feature image',
            'mimetype': 'image/jpeg',
            'license': 'CC-BY',
            'publicShareable': True,
            'url': 'https://example.org/image.jpg',
            'fromSuperEntity': False}],
        'subunits': []}]}
    with patch('histarchexplorer.views.entity.ApiAccess.get_subunits',
               return_value=payload), patch(
            'histarchexplorer.views.entity.get_subunits_root_id',
            return_value=50505):
        feature = authenticated_client.get('/get_entity/1/feature')
        catalogue = authenticated_client.get('/get_entity/1/catalogue')

    assert feature.status_code == 200
    assert catalogue.status_code == 200
    assert b'Feature title' in feature.data
    assert b'feature-1' in catalogue.data
    for response in (feature, catalogue):
        assert b'Feature image' in response.data
        assert b'/view/image/11' in response.data
        assert b'bi-arrows-fullscreen' in response.data
        assert b'License' in response.data
        assert b'CC-BY' in response.data