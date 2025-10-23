from flask import url_for

from histarchexplorer import app


def test_media(client):
    with app.app_context():
        rv = client.get(
            url_for(
            'view_mirador',
            urls="https://thanados.openatlas.eu/api/iiif_manifest/2/128353"))
        assert b"https://thanados.openatlas.eu/" in rv.data
