import json
from typing import Any
from unittest.mock import Mock, patch

import requests
from flask import g

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


def test_execute_search_large_multiple_sources_uses_global_offset(
        app_instance: Any) -> None:
    with app_instance.test_request_context():
        g.case_study_ids = [221174, 198155]
        g.api_headers = {}
        ss = SearchService(app_instance)

        def make_response(case_study_id: int, page: int) -> Mock:
            response = Mock()
            response.raise_for_status.return_value = None
            start = (page - 1) * 100
            response.json.return_value = {
                'data': ([
                    {
                        'id': f'{case_study_id}-{idx}',
                        'name': f'{idx:03}'}
                    for idx in range(start, start + 100)]
                    if page in (1, 15) else []),
                'totalItems': 1500}
            return response

        with patch('requests.get') as mock_get:
            mock_get.side_effect = lambda _url, params, **_kwargs: (
                make_response(
                    params['caseStudy'], int(params['page'])))
            res = ss.execute_search(limit=100, page=30)

        assert res['total_items'] == 3000
        assert len(res['items']) == 100
        assert all(item['caseStudyId'] == 198155 for item in res['items'])
        assert res['items'][0]['id'] == '198155-1400'
        assert res['has_more'] is False
        assert sorted(
            int(call.kwargs['params']['page'])
            for call in mock_get.call_args_list) == [1, 1, 15]


def test_execute_search_small_multiple_sources_sorts_and_slices_page(
        app_instance: Any) -> None:
    with app_instance.test_request_context():
        g.case_study_ids = [221174, 198155]
        g.api_headers = {}
        ss = SearchService(app_instance)
        source_items = {
            221174: [
                {'id': 'a1', 'name': 'Archaeology'},
                {'id': 'a2', 'name': 'Archon'},
                {'id': 'a3', 'name': 'Zeta'}],
            198155: [
                {'id': 'b1', 'name': 'Archive'},
                {'id': 'b2', 'name': 'Beta'},
                {'id': 'b3', 'name': 'Alpha'}]}

        def make_response(case_study_id: int) -> Mock:
            response = Mock()
            response.raise_for_status.return_value = None
            response.json.return_value = {
                'data': source_items[case_study_id],
                'totalItems': 3}
            return response

        with patch('requests.get') as mock_get:
            mock_get.side_effect = lambda _url, params, **_kwargs: (
                make_response(params['caseStudy']))
            res = ss.execute_search(
                query='arch',
                case_study_ids=[221174, 198155],
                limit=2,
                page=2)

        assert [item['name'] for item in res['items']] == [
            'Archon', 'Alpha']
        assert res['total_items'] == 6
        assert res['has_more'] is True
        assert mock_get.call_count == 2


def test_perform_live_search_short_query(app_instance) -> None:
    with app_instance.test_request_context():
        g.case_study_ids = []
        g.api_headers = {}
        ss = SearchService(app_instance)
        assert ss.perform_live_search('te', []) == []
