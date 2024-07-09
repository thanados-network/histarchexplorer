from datetime import datetime
from typing import Optional

from flask import render_template, abort, g, request, redirect, url_for, flash, jsonify, session
from flask_login import current_user, login_required

from histarchexplorer import app


@app.route('/admin/')
@app.route('/admin/<tab>')
@app.route('/admin/<tab>/<entry>')
@login_required
def admin(tab: Optional[str] = None, entry: Optional[str] = None) -> str:
    if current_user.group not in ['admin', 'manager']:
        abort(403)

    g.cursor.execute('SELECT * FROM tng.config ORDER BY name')
    config_data = g.cursor.fetchall()

    g.cursor.execute('SELECT * FROM tng.maps ORDER BY sortorder')
    map_data = g.cursor.fetchall()

    g.cursor.execute('SELECT * FROM tng.config_classes')
    config_classes = g.cursor.fetchall()

    g.cursor.execute('''
        SELECT id, name, domain, range, 'direct' AS direction  FROM tng.config_properties
        UNION ALL
        SELECT id, name_inv, range,domain, 'inverse' AS direction FROM tng.config_properties''')
    config_properties = g.cursor.fetchall()

    mainproject = []
    projects = []
    persons = []
    institutions = []
    roles = []

    for row in config_classes:
        if row.name in ['main-project']:
            mainproject.append(row.id)
        if row.name in ['project']:
            projects.append(row.id)
        if row.name in ['person']:
            persons.append(row.id)
        if row.name in ['institution']:
            institutions.append(row.id)
        if row.name in ['role']:
            roles.append(row.id)

    tabs = [
        {
            'id': 'nav-main-project-tab',
            'label': 'main-project',
            'target': 'nav-main-project',
            'filter': mainproject,
            'id': 5

        },
        {
            'id': 'nav-projects-tab',
            'label': 'projects',
            'target': 'nav-projects',
            'filter': projects,
            'id': 1

        },
        {
            'id': 'nav-persons-tab',
            'label': 'persons',
            'target': 'nav-persons',
            'filter': persons,
            'id': 2
        },
        {
            'id': 'nav-institutions-tab',
            'label': 'institutions',
            'target': 'nav-institutions',
            'filter': institutions,
            'id': 4
        },
        {
            'id': 'nav-attributes-tab',
            'label': 'attributes',
            'target': 'nav-attributes',
            'filter': roles,
            'id': 3
        }
    ]

    g.cursor.execute("""
               SELECT l.id     AS link_id, 
               l.sortorder AS sortorder,
       s.id     AS start_id,
       s.name   AS start_name,
       cp.name  AS config_property,
       cp.id    AS property_id,
       'direct' AS direction,
       e.name   AS end_name,
       e.id     AS end_id,
       r.name   AS role,
       r.id     AS role_id
FROM tng.links l
         JOIN tng.config s ON l.domain_id = s.id
         JOIN tng.config e ON l.range_id = e.id
         JOIN tng.config_properties cp ON l.property = cp.id
         LEFT JOIN tng.config r ON l.attribute = r.id
UNION ALL
SELECT l.id        AS link_id, 
        l.sortorder AS sortorder,
       s.id        AS start_id,
       s.name      AS start_name,
       cp.name_inv AS config_property,
       cp.id       AS property_id,
       'inverse'   AS direction,
       e.name      AS end_name,
       e.id        AS end_id,
       r.name      AS role,
       r.id        AS role_id
FROM tng.links l
         JOIN tng.config s ON l.range_id = s.id
         JOIN tng.config e ON l.domain_id = e.id
         JOIN tng.config_properties cp ON l.property = cp.id
         LEFT JOIN tng.config r ON l.attribute = r.id
         ORDER BY sortorder
    """)
    links_data = g.cursor.fetchall()
    map_id = request.args.get('map_id')

    if map_id:
        g.cursor.execute('SELECT * FROM tng.maps WHERE id = %s', (map_id,))
        map_data = g.cursor.fetchone()

    return render_template("/admin.html", config_data=config_data, tabs=tabs, activetab=tab, activeentry=entry,
                           links_data=links_data, config_properties=config_properties, maps=map_data, map=map)


@app.route('/admin/add_entry', methods=['POST'])
@login_required
def add_entry():
    if current_user.group not in ['admin', 'manager']:
        abort(403)

    category = request.form.get('category')
    current_tab = 'nav-' + category
    name = request.form.get('name')
    description = request.form.get('description')
    address = request.form.get('address')
    mail = request.form.get('mail')
    website = request.form.get('website')
    orcid = request.form.get('orcid')

    config_class_map = {
        'projects': 1,  # option for config_class=2 project vs 1=main_project?
        'persons': 2,
        'institutions': 4,
        'attributes': 3,
        'main-project': 5
    }

    try:
        tab_config_class = config_class_map.get(category)
        if tab_config_class == 5:
            flash(f'Error adding entry {name}: Only one main project allowed', 'danger')
            return redirect(url_for('admin') + current_tab)

        g.cursor.execute('''
                   INSERT INTO tng.config (name, description, address, email, website, orcid_id, config_class)
                   VALUES (
                    NULLIF(%s, ''),
                    NULLIF(%s, ''),
                    NULLIF(%s, ''),
                    NULLIF(%s, ''),
                    NULLIF(%s, ''),
                    NULLIF(%s, ''),
                    %s
                ) RETURNING id
               ''', (name, description, address, mail, website, orcid, tab_config_class))

        new_entry_id = g.cursor.fetchone()[0]

        flash('Entry added successfully!', 'success')
        return redirect(url_for('admin') + current_tab + '/' + current_tab + str(new_entry_id))

    except Exception as e:
        flash(f'Error adding entry {name}: {str(e)}', 'danger')
        return redirect(url_for('admin') + current_tab)

    return redirect(url_for('admin') + current_tab)


@app.route('/admin/delete_entry/<id>/<tab>')
@login_required
def delete_entry(tab: Optional[str] = None, id: Optional[int] = None) -> str:
    if current_user.group not in ['admin', 'manager']:
        abort(403)

    g.cursor.execute(f'SELECT config_class FROM tng.config WHERE id = {id}')
    result = g.cursor.fetchone()
    if result.config_class == 5:
        flash('Main Project cannot be deleted', 'danger')
        return redirect(url_for('admin') + tab)

    g.cursor.execute('DELETE FROM tng.config WHERE id = %(id)s', {'id': int(id)})
    flash('Entry deleted successfully!', 'success')
    return redirect(url_for('admin') + tab)


@app.route('/admin/delete_link/<link_id>/<tab>/<entry>')
@login_required
def delete_link(link_id: Optional[int] = None, tab: Optional[str] = None, entry: Optional[str] = None) -> str:
    if current_user.group not in ['admin', 'manager']:
        abort(403)

    g.cursor.execute('DELETE FROM tng.links WHERE id = %(link_id)s', {'link_id': int(link_id)})
    flash('Link deleted successfully!', 'success')
    return redirect(url_for('admin') + tab + '/' + entry)


@app.route('/admin/add_link/<domain>/<range>/<prop>/<role>/<tab>/<entry>', methods=['GET', 'POST'])
@login_required
def add_link(domain: Optional[int] = None, range: Optional[int] = None, prop: Optional[int] = None,
             role: Optional[int] = None, tab: Optional[str] = None, entry: Optional[str] = None) -> str:
    if current_user.group not in ['admin', 'manager']:
        abort(403)
    g.cursor.execute(
        f'INSERT INTO tng.links (domain_id, range_id, property, attribute) VALUES ({domain}, {range}, {prop}, NULLIF({role}, 0))')
    flash('Link added successfully', 'success')
    return redirect(url_for('admin') + tab + '/' + entry)


@app.route('/edit_entry', methods=['POST', 'GET'])
@login_required
def edit_entry():
    if current_user.group not in ['admin', 'manager']:
        abort(403)

    description = request.form.get('description')
    config_id = request.form.get('config_id')
    current_tab = request.form.get('current_tab')
    current_entry = request.form.get('current_entry')
    name = request.form.get('name')
    address = request.form.get('address')
    mail = request.form.get('mail')
    website = request.form.get('website')
    orcid = request.form.get('orcid')
    legal_note = request.form.get('legalnotice')
    imprint = request.form.get('imprint')

    editsql = """
        UPDATE  tng.config SET 
            description = NULLIF(%(description)s, ''),
            name = NULLIF(%(name)s, ''),
            address = NULLIF(%(address)s, ''),
            email = NULLIF(%(email)s, ''),
            website = NULLIF(%(website)s, ''),
            orcid_id = NULLIF(%(orcid_id)s, ''),
            legal_notice = NULLIF(%(legal_note)s, ''),
            imprint = NULLIF(%(imprint)s, '')
        WHERE  id = %(id)s
    """
    try:
        g.cursor.execute('SELECT id FROM tng.config WHERE id = %(id)s', {'id': int(config_id)})
        result = g.cursor.fetchone()
        if result:
            g.cursor.execute(editsql, {'description': description, 'name': name, 'address': address, 'email': mail,
                                       'website': website, 'orcid_id': orcid, 'id': config_id, 'legal_note': legal_note,
                                       'imprint': imprint})
            flash(f'"{name}" updated successfully', 'success')
        else:
            flash(f'Error updating {name}', 'danger')
    except Exception as e:
        flash(f'Error updating {name}: {str(e)}', 'danger')

    return redirect(url_for('admin') + current_tab + '/' + current_entry)


@app.route('/edit_map', methods=['POST'])
@login_required
def edit_map():
    if current_user.group not in ['admin', 'manager']:
        abort(403)

    name = request.form.get('name')
    display_name = request.form.get('displayname')
    sortorder = request.form.get('inputorder') if request.form.get('inputorder') else ''
    tilestring = request.form.get('description')
    current_tab = request.form.get('current_tab')
    map_id = request.form.get('map_id')

    editsql = """
        UPDATE tng.maps SET
            name = NULLIF(%(name)s, ''),
            display_name = NULLIF(%(display_name)s, ''),
            sortorder = CASE WHEN %(sortorder)s = '' THEN NULL ELSE CAST(%(sortorder)s AS integer) END,
            tilestring = NULLIF(%(tilestring)s, '')
        WHERE id = %(map_id)s
    """

    try:
        g.cursor.execute('SELECT id FROM tng.maps WHERE id = %(map_id)s', {'map_id': map_id})
        result = g.cursor.fetchone()
        if result:
            g.cursor.execute(editsql, {
                'name': name,
                'display_name': display_name,
                'sortorder': sortorder,
                'tilestring': tilestring,
                'map_id': map_id
            })
            flash(f'Map updated successfully', 'map success')
        else:
            flash(f'Error updating map {map_id}', 'map danger')
    except Exception as e:
        flash(f'Error updating map {map_id}: {str(e)}', 'map danger')

    return redirect(url_for('admin'))


@app.route('/admin/add_map', methods=['POST'])
@login_required
def add_map():
    if current_user.group not in ['admin', 'manager']:
        abort(403)

    name = request.form.get('name')
    displayname = request.form.get('displayname')
    inputorder = request.form.get('inputorder')
    description = request.form.get('description')

    try:
        g.cursor.execute('''
            INSERT INTO tng.maps (name, display_name, sortorder, tilestring)
            VALUES (%s, %s, %s, %s) RETURNING id
        ''', (name, displayname, inputorder, description))

        new_map_id = g.cursor.fetchone()[0]

        flash('Map added successfully!', 'map success')
        return redirect(url_for('admin') + '/maps/' + str(new_map_id))

    except Exception as e:
        flash(f'Error adding map {name}: {str(e)}', 'map danger')
        return redirect(url_for('admin') + '/maps')

    return redirect(url_for('admin'))


from flask import flash, redirect, url_for


@app.route('/admin/delete_map/<int:map_id>')
@login_required
def delete_map(map_id: int) -> str:
    if current_user.group not in ['admin', 'manager']:
        abort(403)

    try:
        g.cursor.execute('DELETE FROM tng.maps WHERE id = %(map_id)s', {'map_id': map_id})
        flash('Map deleted successfully!', 'map success')
    except Exception as e:
        flash(f'Error deleting map: {str(e)}', 'map danger')

    return redirect(url_for('admin') + '/maps')


@app.route('/choose_indexBg', methods=['POST'])
def choose_index_bg():
    default_image = '/../static/images/index_map_bg/Blank_map_of_Europe_central_network.png'
    selected_map_id = request.form.get('mapSelection')

    # Fetch maps from database
    g.cursor.execute('SELECT id, display_name, tilestring FROM tng.maps ORDER BY sortorder')
    maps = g.cursor.fetchall()

    if selected_map_id == 'default_image':
        selected_map = default_image
    else:
        try:
            selected_map_id_int = int(selected_map_id)
            selected_map = next((map.tilestring for map in maps if map.id == selected_map_id_int), None)
            if not selected_map:
                selected_map = default_image
        except ValueError:
            selected_map = default_image

    session['selected_map'] = selected_map

    return redirect(url_for('index'))



@app.route('/reset')
@login_required
def reset():
    if current_user.group not in ['admin', 'manager']:
        abort(403)

    g.cursor.execute('''
        DROP SCHEMA IF EXISTS tng CASCADE;
        CREATE SCHEMA IF NOT EXISTS tng;
        
        CREATE TABLE IF NOT EXISTS tng.maps
        (
            id           SERIAL PRIMARY KEY,
            name         TEXT,
            display_name TEXT,
            tilestring   TEXT,
            sortorder     INT   
        );
        
        INSERT INTO tng.maps (name, display_name, tilestring, sortorder) 
            VALUES ('OpenStreetMap', 'Open Street Map', 'L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {maxZoom: 19, attribution: "&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors"});', 1);
        
        CREATE TABLE IF NOT EXISTS tng.config
        (
            id           SERIAL PRIMARY KEY,
            name         TEXT,
            description  TEXT,
            address      TEXT,
            config_class INT,
            email        TEXT,
            orcid_id     TEXT,
            image        TEXT,
            website      TEXT,
            legal_notice TEXT,
            imprint      TEXT,
            language     TEXT DEFAULT 'en'
        );
        
        CREATE TABLE IF NOT EXISTS tng.links
        (
            id        SERIAL PRIMARY KEY,
            domain_id INT,
            range_id  INT,
            property  INT,
            attribute INT,
            sortorder INT
        );
        
        CREATE TABLE IF NOT EXISTS tng.config_classes
        (
            id          SERIAL PRIMARY KEY,
            name        TEXT,
            description TEXT
        );
        
        CREATE TABLE IF NOT EXISTS tng.config_properties
        (
            id          SERIAL PRIMARY KEY,
            name        TEXT,
            name_inv    TEXT,
            description TEXT,
            domain      INT,
            range       INT
        );
        
        ALTER TABLE tng.config
            ADD CONSTRAINT config_config_classes_fk FOREIGN KEY (config_class) REFERENCES tng.config_classes (id);
        ALTER TABLE tng.links
            ADD CONSTRAINT links_config_properties_fk FOREIGN KEY (property) REFERENCES tng.config_properties (id);
        ALTER TABLE tng.links
            ADD CONSTRAINT links_config_fk_domain FOREIGN KEY (domain_id) REFERENCES tng.config (id);
        ALTER TABLE tng.links
            ADD CONSTRAINT links_config_fk_range FOREIGN KEY (range_id) REFERENCES tng.config (id);
        ALTER TABLE tng.links
            ADD CONSTRAINT links_config_fk_role FOREIGN KEY (attribute) REFERENCES tng.config (id);
        
        CREATE OR REPLACE FUNCTION tng.delete_links_on_config_delete()
            RETURNS trigger
            LANGUAGE plpgsql
        AS
        $function$
        BEGIN
            DELETE FROM tng.links WHERE domain_id = OLD.id OR range_id = OLD.id;
            RETURN OLD;
        END;
        $function$;
        
        CREATE TRIGGER delete_links_trigger
            BEFORE DELETE
            ON tng.config
            FOR EACH ROW
        EXECUTE FUNCTION tng.delete_links_on_config_delete();
        
        INSERT INTO tng.config_classes (name) VALUES ('project');
        INSERT INTO tng.config_classes (name) VALUES ('person');
        INSERT INTO tng.config_classes (name) VALUES ('role');
        INSERT INTO tng.config_classes (name) VALUES ('institution');
        INSERT INTO tng.config_classes (name) VALUES ('main-project');
        INSERT INTO tng.config_classes (name) VALUES ('language_code');
        
        INSERT INTO tng.config_properties (name, name_inv, domain, range) VALUES ('has member', 'is member of', (SELECT id FROM tng.config_classes WHERE name = 'project'), (SELECT id FROM tng.config_classes WHERE name = 'person'));
        INSERT INTO tng.config_properties (name, name_inv, domain, range) VALUES ('has affiliation', 'is affiliation of', (SELECT id FROM tng.config_classes WHERE name = 'person'), (SELECT id FROM tng.config_classes WHERE name = 'institution'));
        INSERT INTO tng.config_properties (name, name_inv, domain, range) VALUES ('has translation', 'has translation', NULL, NULL);
        INSERT INTO tng.config_properties (name, name_inv, domain, range) VALUES ('has core member', 'is core member of', (SELECT id FROM tng.config_classes WHERE name = 'main-project'), (SELECT id FROM tng.config_classes WHERE name = 'person'));
        INSERT INTO tng.config_properties (name, name_inv, domain, range) VALUES ('has core institution', 'is core institution of', (SELECT id FROM tng.config_classes WHERE name = 'main-project'), (SELECT id FROM tng.config_classes WHERE name = 'institution'));
        
        INSERT INTO tng.config (name, config_class, description, address, email, website) VALUES ('Main Project', (SELECT id from tng.config_classes WHERE name = 'main-project'), NULL, NULL, NULL, NULL);
        
        INSERT INTO tng.config (name, config_class, description, address, email, website) VALUES ('Stefan Eichert', (SELECT id from tng.config_classes WHERE name = 'person'), NULL, NULL, NULL, NULL);
        INSERT INTO tng.config (name, config_class, description, address, email, website) VALUES ('Lisa Aldrian', (SELECT id from tng.config_classes WHERE name = 'person'), NULL, NULL, NULL, NULL);
        INSERT INTO tng.config (name, config_class, description, address, email, website) VALUES ('David Ruß', (SELECT id from tng.config_classes WHERE name = 'person'), NULL, NULL, NULL, NULL);
        
        INSERT INTO tng.config (name, config_class, description, address, email, website) VALUES ('principial investigator', (SELECT id from tng.config_classes WHERE name = 'role'), NULL, NULL, NULL, NULL);
        INSERT INTO tng.config (name, config_class, description, address, email, website) VALUES ('main coordinator', (SELECT id from tng.config_classes WHERE name = 'role'), NULL, NULL, NULL, NULL);
        INSERT INTO tng.config (name, config_class, description, address, email, website) VALUES ('project researcher', (SELECT id from tng.config_classes WHERE name = 'role'), NULL, NULL, NULL, NULL);
        INSERT INTO tng.config (name, config_class, description, address, email, website) VALUES ('software developer', (SELECT id from tng.config_classes WHERE name = 'role'), NULL, NULL, NULL, NULL);
        INSERT INTO tng.config (name, config_class, description, address, email, website) VALUES ('design & programming', (SELECT id from tng.config_classes WHERE name = 'role'), NULL, NULL, NULL, NULL);
        INSERT INTO tng.config (name, config_class, description, address, email, website) VALUES ('archaeologist', (SELECT id from tng.config_classes WHERE name = 'role'), NULL, NULL, NULL, NULL);
        INSERT INTO tng.config (name, config_class, description, address, email, website) VALUES ('anthropologist', (SELECT id from tng.config_classes WHERE name = 'role'), NULL, NULL, NULL, NULL);
        INSERT INTO tng.config (name, config_class, description, address, email, website) VALUES ('data acquisition', (SELECT id from tng.config_classes WHERE name = 'role'), NULL, NULL, NULL, NULL);
        INSERT INTO tng.config (name, config_class, description, address, email, website) VALUES ('historian', (SELECT id from tng.config_classes WHERE name = 'role'), NULL, NULL, NULL, NULL);
        
        INSERT INTO tng.config (name, config_class, description, address, email, website) VALUES ('sponsor', (SELECT id from tng.config_classes WHERE name = 'role'), NULL, NULL, NULL, 'https://example.exampe');
        INSERT INTO tng.config (name, config_class, description, address, email, website) VALUES ('partner', (SELECT id from tng.config_classes WHERE name = 'role'), NULL, NULL, NULL, 'https://example.exampe');
        
        INSERT INTO tng.config (name, config_class, description, address, email, website) VALUES ('THANADOS', (SELECT id from tng.config_classes WHERE name = 'project'), NULL, NULL, NULL, NULL);
        INSERT INTO tng.config (name, config_class, description, address, email, website) VALUES ('RELIC', (SELECT id from tng.config_classes WHERE name = 'project'), NULL, NULL, NULL, NULL);
        INSERT INTO tng.config (name, config_class, description, address, email, website) VALUES ('REPLICO', (SELECT id from tng.config_classes WHERE name = 'project'), NULL, NULL, NULL, NULL);
        
        INSERT INTO tng.config (name, config_class, description, address, email, website) VALUES ('NHM', (SELECT id from tng.config_classes WHERE name = 'institution'), NULL, NULL, NULL, NULL);
        INSERT INTO tng.config (name, config_class, description, address, email, website) VALUES ('University of Vienna', (SELECT id from tng.config_classes WHERE name = 'institution'), NULL, NULL, NULL, NULL);
        INSERT INTO tng.config (name, config_class, description, address, email, website) VALUES ('Austrian Centre for Digital Humanities & Cultural Heritage', (SELECT id from tng.config_classes WHERE name = 'institution'), NULL, NULL, NULL, NULL);
    ''')

    return redirect(url_for('admin'))


@app.route('/sortlinks', methods=['POST'])
def sortlinks() -> str:
    @login_required
    def reset():
        if current_user.group not in ['admin', 'manager']:
            abort(403)

    data = request.get_json()
    criteria = data['criteria']
    table = data['table']

    print(criteria)
    for row in criteria:
        print(row['order'])
        g.cursor.execute(f'UPDATE tng.{table} SET sortorder = %(order)s  WHERE id = %(id)s',
                         {'id': row['id'], 'order': row['order'], 'table': table})
    return jsonify({'status': 'ok'})
