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


        rv = client.get(url_for('clear_cache'), follow_redirects=True)
        assert b"cache cleared" in rv.data

        rv = client.get(url_for('warm_cache'), follow_redirects=True)
        assert b"cache warmed" in rv.data


        client.get(url_for('reset'))
        rv = client.get(url_for('admin'), follow_redirects=True)
        assert b"reset database" in rv.data


        client.get(
            url_for('check_case_study_id_ajax', entity_id=277452),
            follow_redirects=True)


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

        # rv = client.post(
        #     url_for(
        #     'add_entry',
        #         category='persons',
        #         name='test',
        #         description='testing',
        #         email= 'test@test.org',
        #         orcid_id='2134',
        #         image='https://test.at/'),
        #     follow_redirects=True)
        # assert b'Entry added successfully!' in rv.data

        # rv = client.post(
        #     url_for(
        #     'add_entry',
        #         category='institutions',
        #         name='Institution',
        #         description='desccription',
        #         email= 'test@test.org',
        #         address='Eichertweg 5',
        #         image='https://test.at/',
        #         website='https://nhm.at/'),
        #     follow_redirects=True)
        # assert b'Entry added successfully!' in rv.data

        # rv = client.post(
        #     url_for(
        #     'add_entry',
        #         category='projects',
        #         name='Project',
        #         description='Project description',
        #         case_study= '277452',
        #         website='https://nhm.at/'),
        #     follow_redirects=True)
        # assert b'Entry added successfully!' in rv.data

        # rv = client.get(
        #     url_for(
        #     'add_entry',
        #         category='main_project',
        #         name='test',
        #         description='testing',
        #         email= 'test@test.org',
        #         orcid_id='2134',
        #         image='https://test.at/'))
        # assert b'Only one main project allowed' in rv.data

        rv = client.get(url_for('logout'), follow_redirects=True)
        assert b'ENTITIES' in rv.data
