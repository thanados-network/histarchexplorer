
def test_index_page(client):
    """
    Test that the index page ('/') loads successfully and returns a 200 OK status.
    This test uses the 'client' fixture, which is provided by tests/conftest.py.
    The 'client' fixture gives us a test client for your Flask application,
    allowing us to make requests to your app's endpoints.
    """
    print("\nRunning test_index_page...")
    # Make a GET request to the root URL ('/') of your Flask application
    response = client.get('/')

    # Assert that the HTTP status code of the response is 200 (OK)
    assert response.status_code == 200

    # Assert that the byte string 'Entities' is present in the response data.
    # The response.data attribute contains the raw bytes of the response body.
    assert b"ENTITIES" in response.data

    print("test_index_page completed successfully.")
