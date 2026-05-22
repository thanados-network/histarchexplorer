import json
import pytest
from flask import g
import requests
from unittest.mock import MagicMock, patch
from histarchexplorer.api.presentation_view import (
    PresentationView, FeatureModel, EntityTypeModel, Relation, File, Reference,
    ExternalReferenceModel)
from histarchexplorer import app

@pytest.fixture
def mock_g_divisions():
    with app.test_request_context():
        g.type_divisions = {
            "Grave": {"ids": [1], "icon_type": "icon", "icon_value": "grave.png"},
            "Building": {"ids": [2], "icon_type": "bootstrap", "icon_value": "bi-house"}
        }
        yield

def test_to_json():
    pv = PresentationView(
        id=1, system_class="Site", view_class="site", title="Test Site",
        description={"en": "Test"}, aliases=["Test"], start="2023", end="2024"
    )
    res = pv.to_json()
    data = json.loads(res)
    assert data["id"] == 1
    assert data["systemClass"] == "Site"

def test_parse_geometries():
    geom_data = {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [10, 20]},
        "properties": {
            "locationId": 1, "entityId": 2, "title": "T", "description": "D", "shapeType": "S"
        }
    }
    res = PresentationView.parse_geometries(geom_data, "Site")
    assert len(res) == 1
    assert res[0].geometry.type == "Point"
    
    collection = {"type": "FeatureCollection", "features": [geom_data]}
    res = PresentationView.parse_geometries(collection, "Site")
    assert len(res) == 1
    
    assert PresentationView.parse_geometries(None, "Site") == []

def test_parse_time_range():
    when = {
        "start": {"earliest": "2023", "latest": "2023"},
        "end": {"earliest": "2024", "latest": "2024"}
    }
    res = PresentationView.parse_time_range(when)
    assert res.start.earliest == "2023"
    assert res.end.earliest == "2024"
    assert PresentationView.parse_time_range(None) is None

def test_parse_types(mock_g_divisions):
    types_data = [
        {
            "id": 1, "title": "Grave", "isStandard": True,
            "typeHierarchy": [{"identifier": "types/1", "label": "Grave", "descriptions": "D"}]
        }
    ]
    res = PresentationView.parse_types(types_data)
    assert len(res) == 1
    assert res[0].id == 1
    assert res[0].division["label"] == "Grave"

def test_parse_relations():
    raw_relations = {
        "Site": [
            {
                "id": 1, "title": "Related", "systemClass": "Site",
                "relationTypes": ["child"], "description": "Desc",
                "standardType": {"id": 1, "title": "Type"}
            }
        ]
    }
    res = PresentationView.parse_relations(raw_relations)
    assert "Site" in res
    assert len(res["Site"]) == 1
    assert res["Site"][0].id == 1

def test_parse_files():
    with app.test_request_context():
        files_data = [
            {
                "id": 1, "title": "file.jpg", "mimetype": "image/jpeg",
                "license": "CC-BY", "publicShareable": True
            }
        ]
        res = PresentationView.parse_file(files_data)
        assert len(res) == 1
        assert res[0].title == "file.jpg"
        assert res[0].render_type == "image"

def test_parse_references():
    ref_data = [{"id": 1, "reference": "Author 2023", "pages": "10"}]
    res = PresentationView.merge_references(ref_data)
    assert len(res) == 1
    assert res[0]["id"] == 1

def test_external_reference_from_dict():
    data = {
        "id": "1", "type": "T", "identifier": "I", "referenceSystem": "S",
        "resolverURL": "R", "referenceURL": "U"
    }
    er = ExternalReferenceModel.from_dict(data)
    assert er.id == "1"

def test_reference_from_dict():
    data = {
        "id": "1", "title": "T", "systemClass": "C", "type": "Y",
        "typeId": 2, "citation": "Ci", "pages": "P"
    }
    ref = Reference.from_dict(data)
    assert ref.id == "1"

def test_merge_references_complex():
    ref_data = [
        {"id": 1, "reference": "Ref 1", "pages": "10"},
        {"id": 1, "reference": "Ref 1", "pages": "20"}
    ]
    res = PresentationView.merge_references(ref_data)
    assert len(res) == 1

def test_from_api_errors(app_instance):
    with app_instance.test_request_context():
        g.api_headers = {}
        with patch('requests.get') as mock_get:
            # HTTP Error
            mock_get.side_effect = requests.exceptions.HTTPError("404")
            with pytest.raises(requests.exceptions.HTTPError):
                PresentationView.from_api(1)
            
            # JSON error
            mock_get.side_effect = None
            mock_get.return_value.json.side_effect = ValueError("JSON error")
            with pytest.raises(ValueError):
                PresentationView.from_api(1)

def test_presentation_view_parse_geometries_empty(app_instance):
    with app_instance.test_request_context():
        res = PresentationView.parse_geometries({}, "class")
        assert res == []

def test_presentation_view_parse_relations_empty():
    res = PresentationView.parse_relations({})
    assert res == {}
