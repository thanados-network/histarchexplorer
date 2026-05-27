import pytest
from unittest.mock import patch, MagicMock
from flask import g
from histarchexplorer.models.search import SearchService
import json
import requests

def test_search_service_api_errors(app_instance):
    with app_instance.test_request_context():
        g.view_classes = {}
        g.api_headers = {}
        ss = SearchService(app_instance)
        
        with patch('requests.get') as mock_get:
            # HTTP Error
            mock_get.side_effect = requests.exceptions.HTTPError("404")
            assert ss.perform_search("test", "all", []) == []
            
            # JSON Decode Error
            mock_get.side_effect = None
            mock_get.return_value.json.side_effect = json.JSONDecodeError("msg", "doc", 0)
            assert ss.perform_search("test", "all", []) == []
            
            # Unexpected Exception
            mock_get.side_effect = Exception("Unexpected")
            assert ss.perform_search("test", "all", []) == []

def test_perform_search_with_classes(app_instance):
    with app_instance.test_request_context():
        g.view_classes = {}
        g.api_headers = {}
        ss = SearchService(app_instance)
        with patch('requests.get') as mock_get:
            mock_get.return_value.json.return_value = {"results": [{"id": 1}]}
            res = ss.perform_search("test", "category", ["class1", "class2"])
            assert len(res) == 2
            assert mock_get.call_count == 2

def test_get_entity_detail_errors(app_instance):
    with app_instance.test_request_context():
        g.view_classes = {}
        g.api_headers = {}
        ss = SearchService(app_instance)
        with patch('requests.get') as mock_get:
            # HTTP Error
            mock_get.side_effect = requests.exceptions.HTTPError("404")
            assert ss.get_entity_detail(1) is None
            
            # JSON Decode Error
            mock_get.side_effect = None
            mock_get.return_value.json.side_effect = json.JSONDecodeError("msg", "doc", 0)
            assert ss.get_entity_detail(1) is None
            
            # Unexpected Exception
            mock_get.side_effect = Exception("Unexpected")
            assert ss.get_entity_detail(1) is None

def test_perform_live_search_short_query(app_instance):
    with app_instance.test_request_context():
        g.view_classes = {}
        g.api_headers = {}
        ss = SearchService(app_instance)
        assert ss.perform_live_search("te", []) == []
