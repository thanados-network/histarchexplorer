from flask.testing import FlaskClient
from histarchexplorer.models.user import User
from unittest.mock import patch
from bcrypt import hashpw, gensalt


def test_login_page(client: FlaskClient) -> None:
    rv = client.get('/login')
    assert rv.status_code == 200


def test_login_success(client: FlaskClient) -> None:
    password = 'testpassword'
    hashed = hashpw(password.encode('utf-8'), gensalt()).decode('utf-8')
    
    mock_user = User({
        'id': 1,
        'active': 1,
        'username': 'testuser',
        'password': hashed,
        'group_name': 'admin',
        'real_name': 'Test User'
    })

    with patch('histarchexplorer.models.user.User.get_by_username',
               return_value=mock_user), \
         patch('histarchexplorer.views.login.login_user') as mock_login_user:
        rv = client.post('/login', data={
            'username': 'testuser',
            'password': password,
            'save': 'login'
        })
        assert rv.status_code == 302
        assert mock_login_user.called


def test_login_invalid_password(client: FlaskClient) -> None:
    password = 'testpassword'
    hashed = hashpw(password.encode('utf-8'), gensalt()).decode('utf-8')

    mock_user = User({
        'id': 1,
        'active': 1,
        'username': 'testuser',
        'password': hashed,
        'group_name': 'admin',
        'real_name': 'Test User'
    })

    with patch('histarchexplorer.models.user.User.get_by_username',
               return_value=mock_user):
        rv = client.post('/login', data={
            'username': 'testuser',
            'password': 'wrongpassword',
            'save': 'login'
        })
        assert rv.status_code == 200
        # Should show flash message, but we just check it didn't redirect


def test_login_inactive_user(client: FlaskClient) -> None:
    password = 'testpassword'
    hashed = hashpw(password.encode('utf-8'), gensalt()).decode('utf-8')

    mock_user = User({
        'id': 1,
        'active': 0,
        'username': 'testuser',
        'password': hashed,
        'group_name': 'admin',
        'real_name': 'Test User'
    })

    with patch('histarchexplorer.models.user.User.get_by_username',
               return_value=mock_user):
        rv = client.post('/login', data={
            'username': 'testuser',
            'password': password,
            'save': 'login'
        })
        assert rv.status_code == 200


def test_login_nonexistent_user(client: FlaskClient) -> None:
    with patch('histarchexplorer.models.user.User.get_by_username',
               return_value=None):
        rv = client.post('/login', data={
            'username': 'nonexistent',
            'password': 'password',
            'save': 'login'
        })
        assert rv.status_code == 200


def test_logout_authenticated(authenticated_client: FlaskClient) -> None:
    rv = authenticated_client.get('/logout')
    assert rv.status_code == 302
    assert rv.location == '/'


def test_logout_unauthenticated(client: FlaskClient) -> None:
    rv = client.get('/logout', follow_redirects=False)
    assert rv.status_code == 302
    assert '/login' in rv.location
