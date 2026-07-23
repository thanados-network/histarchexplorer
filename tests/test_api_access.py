from unittest.mock import MagicMock, patch

import pytest
import requests
from flask import g

from histarchexplorer import app, cache
from histarchexplorer.api.api_access import ApiAccess, PROXIES


@pytest.fixture(autouse=True)
def clear_subunits_cache():
    cache.delete_memoized(ApiAccess.get_subunits)
    yield
    cache.delete_memoized(ApiAccess.get_subunits)


def test_get_subunits_fetches_and_caches_hierarchy():
    response = MagicMock()
    response.json.return_value = {'features': []}
    with app.test_request_context():
        g.api_headers = {'Authorization': 'Bearer test'}
        with patch('histarchexplorer.api.api_access.requests.get',
                   return_value=response) as mock_get:
            assert ApiAccess.get_subunits(50505) == {'features': []}
            assert ApiAccess.get_subunits(50505) == {'features': []}

    mock_get.assert_called_once_with(
        f"{app.config['API_URL']}subunits/50505",
        headers={'Authorization': 'Bearer test'},
        proxies=PROXIES,
        timeout=30)
    response.raise_for_status.assert_called_once_with()


def test_get_subunits_raises_for_failed_response():
    response = MagicMock()
    response.raise_for_status.side_effect = requests.HTTPError('not found')
    with app.test_request_context():
        g.api_headers = {}
        with patch('histarchexplorer.api.api_access.requests.get',
                   return_value=response):
            with pytest.raises(requests.HTTPError):
                ApiAccess.get_subunits(50505)
    response.json.assert_not_called()