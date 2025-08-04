from flask import url_for

from histarchexplorer import app


def test_admin_page(client):
    with app.app_context():
        rv = client.get(url_for('admin'), follow_redirects=True)
        assert b"Username" in rv.data

        client.post(
                url_for('login'),
                data={'username': 'Alice', 'password': 'test'})
        rv = client.get(url_for('admin'), follow_redirects=True)
        assert b"TOOLS" in rv.data

        client.get(url_for('reset'))
        rv = client.get(url_for('admin'), follow_redirects=True)
        assert b"reset database" in rv.data


        client.post(
                url_for('deselect_entities'),
                data={'selected_entities': ['source', 'external_reference']})
        rv = client.get(url_for('admin'), follow_redirects=True)
        assert b"set hidden entities" in rv.data

        client.post(
                url_for('select_entities'),
                data={'selected_entities': ['source', 'external_reference']})
        rv = client.get(url_for('admin'), follow_redirects=True)
        assert b"set shown entities" in rv.data

        client.post(
                url_for('update_case_study_id', id_=8240),
                data={'selected_entities': ['source', 'external_reference']})
        rv = client.get(url_for('admin'), follow_redirects=True)
        assert b"updated case study id successfully" in rv.data

        client.post(
                url_for('update_case_study_id', id_=50505),
                data={'selected_entities': ['source', 'external_reference']})
        rv = client.get(url_for('admin'), follow_redirects=True)
        assert b"Invalid Case Study ID" in rv.data

        rv = client.get(
            url_for(
            'add_link',
                domain='1',
                range='3',
                property='3',
                role='2',
                sortorder='5'),
            follow_redirects=True)
        assert b'Link added successfully' in rv.data

        rv = client.get(
            url_for(
            'delete_link',
                link_id='8',
                tab='nav-persons',
                entry='nav-persons2'),
            follow_redirects=True)
        assert b'Link deleted successfully' in rv.data

        rv = client.get(url_for('logout'), follow_redirects=True)
        assert b'ENTITIES' in rv.data
