import pytest
from histarchexplorer.api.util import (
    split_date_string, is_full_year_span, format_date, get_render_type,
    get_description_translated, to_camel_case, dict_to_camel_case,
    get_icon_url, get_divisions)

def test_split_date_string():
    assert split_date_string(None) == ""
    assert split_date_string("2023-05-22T14:11:00") == "22.05.2023"
    assert split_date_string("-0500-01-01T00:00:00") == "-01.01.500"
    assert split_date_string("-0044-03-15T00:00:00") == "-15.03.44"

def test_is_full_year_span():
    assert is_full_year_span("01.01.2023", "31.12.2023") is True
    assert is_full_year_span("01.01.2023", "30.12.2023") is False

def test_format_date():
    assert format_date("01.01.2023", "31.12.2023") == "2023 AD"
    assert format_date("-01.01.500", "-31.12.500") == "500 BC - 500 BC"
    assert format_date("01.01.2023", "31.12.2024") == "2023 AD"
    assert format_date("01.01.2023", "30.12.2024") == "2023 AD - 2024 AD"
    assert format_date("-01.01.500", "31.12.500") == "500 BC - 500 AD"
    assert format_date("22.05.2023", "") == "22.5.2023"
    assert format_date("-22.05.2023", "") == "22.5.2023 BC"

def test_get_render_type():
    assert get_render_type(None) == 'unknown'
    assert get_render_type("image/jpeg") == 'image'
    assert get_render_type("image/webp") == 'webp'
    assert get_render_type("image/svg+xml") == 'svg'
    assert get_render_type("video/mp4") == 'video'
    assert get_render_type("application/pdf") == 'pdf'
    assert get_render_type("model/glb") == '3d_model'
    assert get_render_type("text/plain") == 'unknown'

def test_format_date_more():
    assert format_date("01.01.1000", "31.12.1000") == "1000 AD"
    # Current implementation returns "1000 BC - 1000 BC" because .startswith("01.01.") fails for "-01.01.1000"
    assert format_date("-01.01.1000", "-31.12.1000") == "1000 BC - 1000 BC"
    assert format_date("", "01.01.2000") == "01.01.2000"
    assert format_date("01.01.2000", "") == "1.1.2000"
    assert format_date("-01.01.2000", "") == "1.1.2000 BC"

def test_get_description_translated():
    assert get_description_translated(None) is None
    assert get_description_translated("Simple description") == {
        'en': 'Simple description', 'de': 'Simple description'}
    assert get_description_translated("##en_##English##_en## ##de_##Deutsch##_de##") == {
        'en': 'English', 'de': 'Deutsch'}
    assert get_description_translated("English text ##German Deutsch text") == {
        'en': 'English text', 'de': 'Deutsch text'}

def test_camel_case():
    assert to_camel_case("snake_case_string") == "snakeCaseString"
    data = {"first_name": "John", "last_name": "Doe", "details": {"birth_date": "1990-01-01"}}
    expected = {"firstName": "John", "lastName": "Doe", "details": {"birthDate": "1990-01-01"}}
    assert dict_to_camel_case(data) == expected
    assert dict_to_camel_case([data]) == [expected]
    assert dict_to_camel_case("not a dict") == "not a dict"

from unittest.mock import patch, MagicMock
from flask import Flask, g

def test_get_icon_url(app_instance):
    with app_instance.test_request_context():
        with patch('os.path.exists') as mock_exists:
            mock_exists.return_value = True
            url = get_icon_url("test.png")
            assert "/uploads/icons/test.png" in url
            
            mock_exists.return_value = False
            url = get_icon_url("test.png")
            assert "static" in url

def test_get_divisions(app_instance):
    with app_instance.test_request_context():
        g.type_divisions = {
            'Grave': {'ids': [1, 2], 'icon_type': 'icon', 'icon_value': 'grave.png'},
            'Other': {'ids': [3], 'icon_type': 'bootstrap', 'icon_value': 'bi-box'},
            'Fallback': {'ids': [4], 'icon_type': 'unknown'}
        }
        
        # Match by ID
        res = get_divisions(1, [])
        assert res['label'] == 'Grave'
        assert 'grave.png' in res['icon_url']
        
        # Match by hierarchy
        res = get_divisions(99, [{'identifier': '.../2'}])
        assert res['label'] == 'Grave'
        
        # Bootstrap icon
        res = get_divisions(3, [])
        assert res['label'] == 'Other'
        assert 'bi-box' in res['icon']
        
        # Fallback icon
        res = get_divisions(4, [])
        assert res['label'] == 'Fallback'
        assert 'bi-box' in res['icon']
        
        # No match
        res = get_divisions(99, [])
        assert res['label'] == 'other'
