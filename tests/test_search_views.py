from unittest.mock import patch

from flask.testing import FlaskClient


def test_search_page(authenticated_client: FlaskClient) -> None:
    rv = authenticated_client.get('/search?q=Thunau&startDate=700&endDate=900')
    assert rv.status_code == 200
    html = rv.get_data(as_text=True)
    assert 'searchAppRoot' in html
    assert 'timespanSliderMin' in html
    assert 'caseStudyPills' in html
    assert 'entityClassPills' in html
    assert 'searchResultsTable' in html


def test_api_search_endpoint(authenticated_client: FlaskClient) -> None:
    with patch(
            'histarchexplorer.models.search.SearchService.execute_search'
    ) as mock_exec:
        mock_exec.return_value = {
            'items': [{
                'id': '119152',
                'name': 'Thunau Burial Mounds',
                'systemClass': 'place',
                'timespanDisplay': '800 – 850'}],
            'total_items': 1,
            'page': 1,
            'limit': 50,
            'has_more': False}
        rv = authenticated_client.get(
            '/api/search?search=Thunau&caseStudy=221174'
            '&entityClass=place&startDate=700&endDate=900')
        assert rv.status_code == 200
        payload = rv.get_json()
        assert payload['total_items'] == 1
        assert payload['items'][0]['name'] == 'Thunau Burial Mounds'
        mock_exec.assert_called_once()
        call_kwargs = mock_exec.call_args.kwargs
        assert call_kwargs['query'] == 'Thunau'
        assert call_kwargs['case_study_ids'] == [221174]
        assert call_kwargs['entity_classes'] == ['place']
        assert call_kwargs['start_date'] == '700'
        assert call_kwargs['end_date'] == '900'


def test_search_live(authenticated_client: FlaskClient) -> None:
    with patch(
            'histarchexplorer.models.search.SearchService.perform_live_search'
    ) as mock_search:
        mock_search.return_value = [{'id': '1', 'name': 'Live Result'}]
        rv = authenticated_client.get('/search_live?q=test')
        assert rv.status_code == 200
        assert rv.get_json()[0]['name'] == 'Live Result'
