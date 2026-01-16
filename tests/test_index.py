from flask.testing import FlaskClient


def test_index_page(client: FlaskClient) -> None:
    rv = client.get('/')
    assert rv.status_code == 200
    assert b"SEARCH" in rv.data


def test_set_language_view(client: FlaskClient) -> None:
    test_language = 'de'
    referrer_url = '/'
    response = client.get(
        f'/language={test_language}',
        headers={'Referer': referrer_url})
    assert response.status_code == 302
    assert response.location == referrer_url
    with client.session_transaction() as session:
        assert session['language'] == test_language
