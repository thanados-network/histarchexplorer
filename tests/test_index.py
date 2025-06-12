
def test_index_page(client):
    """
    Test that the index page ('/') loads successfully and returns a 200 OK status.
    This test uses the 'client' fixture, which is provided by tests/conftest.py.
    The 'client' fixture gives us a test client for your Flask application,
    allowing us to make requests to your app's endpoints.
    """
    rv = client.get('/')
    assert rv.status_code == 200
    assert b"SEARCH" in rv.data



def test_set_language_view(client):
    """
    Test the /language=<language> view to ensure it sets the session language
    and redirects correctly.
    """
    test_language = 'de'
    referrer_url = '/'
    response = client.get(
        f'/language={test_language}',
        headers={'Referer': referrer_url})
    assert response.status_code == 302
    assert response.location == referrer_url
    with client.session_transaction() as session:
        assert session['language'] == test_language


