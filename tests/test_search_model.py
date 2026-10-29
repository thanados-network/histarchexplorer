import json
from unittest.mock import patch

from flask import g
import requests

from histarchexplorer.models.search import (
    SearchService, format_search_timespan, sanitize_date_param)


def test_format_search_timespan() -> None:
    assert format_search_timespan(None) == ''
    assert format_search_timespan({
        'start': {
            'earliest': '0800-01-01T00:00:00',
            'latest': '0800-12-31T00:00:00',
            'comment': None},
        'end': {
            'earliest': '0850-01-01T00:00:00',
            'latest': '0850-12-31T00:00:00',
            'comment': None}}) == '800 – 850'
    assert format_search_timespan({
        'start': {
            'earliest': '-0800-01-01T00:00:00',
            'latest': '-0800-12-31T00:00:00',
            'comment': 'ca.'},
        'end': {
            'earliest': '-0500-01-01T00:00:00',
            'latest': '-0500-12-31T00:00:00',
            'comment': None}}) == 'ca. 800 BC – 500 BC'


def test_sanitize_date_param() -> None:
    assert sanitize_date_param(None) is None
    assert sanitize_date_param('  ') is None
    assert sanitize_date_param('-800') == '-800'
    assert sanitize_date_param('1050') == '1050'
    assert sanitize_date_param('0800-01-01') == '0800-01-01'
    assert sanitize_date_param('invalid-date') is None


def test_search_service_api_errors(app_instance) -> None:
    with app_instance.test_request_context():
        g.case_study_ids = [221174]
        g.api_headers = {}
        ss = SearchService(app_instance)

        with patch('requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.HTTPError('404')
            res = ss.execute_search(query='test')
            assert res['items'] == []
            assert res['total_items'] == 0

            mock_get.side_effect = None
            mock_get.return_value.json.side_effect = json.JSONDecodeError(
                'msg', 'doc', 0)
            res = ss.execute_search(query='test')
            assert res['items'] == []

            mock_get.side_effect = Exception('Unexpected')
            res = ss.execute_search(query='test')
            assert res['items'] == []


def test_execute_search_with_filters(app_instance) -> None:
    with app_instance.test_request_context():
        g.case_study_ids = [221174, 198155]
        g.api_headers = {}
        ss = SearchService(app_instance)
        with patch('requests.get') as mock_get:
            mock_get.return_value.json.return_value = {
                'data': [{
                    'id': 119152,
                    'name': 'Thunau Burial Mounds',
                    'systemClass': 'place',
                    'timespan': {
                        'start': {
                            'earliest': '0800-01-01T00:00:00',
                            'latest': '0800-12-31T00:00:00',
                            'comment': None},
                        'end': {
                            'earliest': '0850-01-01T00:00:00',
                            'latest': '0850-12-31T00:00:00',
                            'comment': None}}}],
                'totalItems': 1}
            res = ss.execute_search(
                query='Thunau',
                entity_classes=['place', 'artifact'],
                case_study_ids=[221174],
                start_date='700',
                end_date='1000',
                sort_by='start_date',
                sort_order='desc',
                limit=25,
                page=1)
            assert mock_get.call_count == 2
            assert len(res['items']) == 1
            assert res['items'][0]['id'] == '119152'
            assert res['items'][0]['timespanDisplay'] == '800 – 850'
            assert res['items'][0]['caseStudyId'] == 221174


def test_perform_live_search_short_query(app_instance) -> None:
    with app_instance.test_request_context():
        g.case_study_ids = []
        g.api_headers = {}
        ss = SearchService(app_instance)
        assert ss.perform_live_search('te', []) == []
