from unittest.mock import patch, MagicMock

import pytest
from flask.testing import FlaskClient

from histarchexplorer import app
from histarchexplorer.models.user import User
from tests.base import reset_test_database

app.config.from_pyfile('testing.py')


@pytest.fixture(scope='session', autouse=True)
def setup_database() -> None:
    reset_test_database()


@pytest.fixture()
def client() -> FlaskClient:
    with app.test_client() as client:
        yield client


@pytest.fixture()
def authenticated_client() -> FlaskClient:
    mock_user = MagicMock(spec=User)
    mock_user.is_authenticated = True
    mock_user.is_active = True
    mock_user.is_anonymous = False
    mock_user.id = 1
    mock_user.username = 'test'
    mock_user.group = 'admin'
    mock_user.real_name = 'Test User'
    mock_user.get_id.return_value = '1'

    with app.test_client() as client:
        with patch(
            'histarchexplorer.views.login.load_user',
            return_value=mock_user
        ), patch(
            'flask_login.utils._get_user',
            return_value=mock_user
        ):
            yield client
