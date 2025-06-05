import json
from typing import Optional

from flask import (
    render_template, abort, g, request, redirect, url_for,
    flash, session)
from flask_login import current_user, login_required
from flask_babel import lazy_gettext as _
from setuptools.windows_support import hide_file
from werkzeug import Response

from histarchexplorer import app
from histarchexplorer.api.helpers import get_entities_count_by_case_study
from histarchexplorer.database.config import (
    get_config_data, update_jsonb_column)
from histarchexplorer.database.config_classes import get_config_classes
from histarchexplorer.database.config_properties import get_config_properties
from histarchexplorer.database.map import get_base_map, get_base_map_by_id
from histarchexplorer.database.settings import (
    get_map_settings, get_shown_entities, get_hidden_entities)
from histarchexplorer.utils import helpers


@app.route('/admin/')
@app.route('/admin/<tab>')
@app.route('/admin/<tab>/<entry>')
@login_required
def admin(tab: Optional[str] = None, entry: Optional[str] = None) -> str:
    if current_user.group not in ['admin', 'manager']:
        abort(403)

    # todo: this will be obsolete if we change to dict instead to named tuples
    language = session.get(
        'language',
        request.accept_languages.best_match(app.config['LANGUAGES'].keys()))

    entities = []
    for item in get_config_data(language):
        entity = {'id': item.id, 'config_class': item.config_class,
                  'website': item.website, 'email': item.email,
                  'orcid_id': item.orcid_id, 'image': item.image}

        for column in ['name', 'description', 'imprint', 'address',
                       'legal_notice']:
            entity[column] = {}
            if getattr(item, column):
                for key, value in getattr(item, column).items():
                    entity[column][key] = value
                entity[column]['display'] = helpers.get_translation(
                    entity[column])

        entities.append(entity)

    # todo: this will be obsolete if we change to dict instead to named tuples
    config_properties = get_config_properties()
    colnames = [desc[0] for desc in g.cursor.description]
    config_list = [dict(zip(colnames, row)) for row in config_properties]

    for row in config_list:
        row['name'] = helpers.get_translation(row['name'])

    mainproject = []
    projects = []
    persons = []
    institutions = []
    roles = []

    for row in get_config_classes():
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
            'label': _('main-project'),
            'target': 'nav-main-project',
            'filter': mainproject,
            'id': 5

        },
        {
            'label': _('projects'),
            'target': 'nav-projects',
            'filter': projects,
            'id': 1

        },
        {
            'label': _('persons'),
            'target': 'nav-persons',
            'filter': persons,
            'id': 2
        },
        {
            'label': _('institutions'),
            'target': 'nav-institutions',
            'filter': institutions,
            'id': 4
        },
        {
            'label': _('attributes'),
            'target': 'nav-attributes',
            'filter': roles,
            'id': 3
        }
    ]
    #print(tabs)

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

    colnames = [desc[0] for desc in g.cursor.description]

    links_list = [dict(zip(colnames, row)) for row in links_data]

    for row in links_list:
        row['start_name'] = helpers.get_translation(row['start_name'])
        row['end_name'] = helpers.get_translation(row['end_name'])
        row['config_property'] = helpers.get_translation(
            row['config_property'])
        row['role'] = helpers.get_translation(row['role'])

    map_data = get_base_map()
    if map_id := request.args.get('map_id'):
        # Todo: int(map_id) can create problems. Find use case.
        map_data = get_base_map_by_id(int(map_id))

    map_settings = get_map_settings()
    settings = {
        'img': map_settings.index_img,
        'map': map_settings.index_map,
        'img_map': map_settings.img_map,
        'greyscale': map_settings.greyscale,
        'not_sel': 'map' if map_settings.img_map == 'image' else 'image'}

    class_items = get_entities_count_by_case_study()
    entities_dict = {k: v for k, v in class_items.items() if
                     k not in app.config['CLASSES_TO_SKIP']}

    shown_entities = get_shown_entities()
    hidden_entities = get_hidden_entities()

    view_classes = app.config['VIEW_CLASSES']

    return render_template(
        "admin.html",
        config_data=entities,
        entities=entities,
        tabs=tabs,
        activetab=tab,
        activeentry=entry,
        links_data=links_list,
        config_properties=config_list,
        maps=map_data,
        settings=settings,
        class_items=entities_dict,
        shown_entities=shown_entities,
        hidden_entities=hidden_entities,
        view_classes=view_classes)


@app.route('/admin/add_entry', methods=['POST'])
@login_required
def add_entry() -> Response:
    if current_user.group not in ['admin', 'manager']:
        abort(403)
    language = session.get(
        'language',
        request.accept_languages.best_match(app.config['LANGUAGES'].keys()))
    category = request.form.get('category') or ''
    current_tab = 'nav-' + category
    description = request.form.get('description') or ''
    name = request.form.get('name') or ''
    address = request.form.get('address') or ''
    mail = request.form.get('mail') or ''
    website = request.form.get('website') or ''
    orcid = request.form.get('orcid') or ''
    legal_notice = request.form.get('legalnotice') or ''
    imprint = request.form.get('imprint') or ''
    image = request.form.get('image') or ''

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
            flash(f'Error adding entry {name}: Only one main project allowed',
                  'danger')
            return redirect(url_for('admin') + current_tab)

        g.cursor.execute('''
                   INSERT INTO tng.config (name, email, website, orcid_id, 
                   image, config_class)
                   VALUES (
                    '{"de": "Stefan Eichert", "en": "Stefan Eichert"}'::jsonb,
                    NULLIF(%s, ''),
                    NULLIF(%s, ''),
                    NULLIF(%s, ''),
                    NULLIF(%s, ''),
                    %s
                ) RETURNING id
               ''', (mail, website, orcid, image, tab_config_class))

        new_entry_id = g.cursor.fetchone()[0]
        config_id = new_entry_id

        update_jsonb_column('name', name, language, config_id)
        update_jsonb_column('address', address, language, config_id)
        update_jsonb_column('description', description, language, config_id)
        update_jsonb_column('imprint', imprint, language, config_id)
        update_jsonb_column('legal_notice', legal_notice, language, config_id)

        flash('Entry added successfully!', 'success')
        return redirect(
            url_for('admin') + current_tab + '/' + current_tab + str(
                new_entry_id))

    except Exception as e:
        flash(f'Error adding entry {name}: {str(e)}', 'danger')
        return redirect(url_for('admin') + current_tab)

    # return redirect(url_for('admin') + current_tab)


@app.route('/admin/delete_entry/<id>/<tab>')
@login_required
def delete_entry(tab: str, id_: int) -> Response:
    if current_user.group not in ['admin', 'manager']:
        abort(403)

    g.cursor.execute(f'SELECT config_class FROM tng.config WHERE id = {id_}')
    result = g.cursor.fetchone()
    if result.config_class == 5:
        flash('Main Project cannot be deleted', 'danger')
        return redirect(url_for('admin') + tab)

    g.cursor.execute('DELETE FROM tng.config WHERE id = %(id)s',
                     {'id': int(id_)})
    flash('Entry deleted successfully!', 'success')
    return redirect(url_for('admin') + tab)


@app.route('/admin/delete_link/<link_id>/<tab>/<entry>')
@login_required
def delete_link(link_id: int,  tab: str, entry: str) -> Response:
    if current_user.group not in ['admin', 'manager']:
        abort(403)

    g.cursor.execute('DELETE FROM tng.links WHERE id = %(link_id)s',
                     {'link_id': int(link_id)})
    flash('Link deleted successfully!', 'success')
    return redirect(url_for('admin') + tab + '/' + entry)


@app.route('/admin/add_link/<domain>/<range_>/<prop>/<role>/<tab>/<entry>',
           methods=['GET', 'POST'])
@login_required
def add_link(
        domain: int,
        range_: int,
        prop: int,
        role: int,
        tab: str,
        entry: str) -> Response:
    if current_user.group not in ['admin', 'manager']:
        abort(403)
    g.cursor.execute(
        f'INSERT INTO tng.links (domain_id, range_id, property, attribute, sortorder) '
        f'VALUES ({domain}, {range_}, {prop}, NULLIF({role}, 0), COALESCE((SELECT (sortorder + 1) FROM tng.links WHERE sortorder IS NOT NULL ORDER BY sortorder DESC LIMIT 1),1))')
    flash('Link added successfully', 'success')
    return redirect(url_for('admin') + tab + '/' + entry)


@app.route('/edit_entry', methods=['POST', 'GET'])
@login_required
def edit_entry() -> Response:
    if current_user.group not in ['admin', 'manager']:
        abort(403)

    language = session.get(
        'language',
        request.accept_languages.best_match(
            app.config['LANGUAGES'].keys()))

    description = request.form.get('description') or ''
    config_id = request.form.get('config_id') or ''
    current_tab = request.form.get('current_tab') or ''
    current_entry = request.form.get('current_entry') or ''
    name = request.form.get('name') or ''
    address = request.form.get('address') or ''
    mail = request.form.get('mail') or ''
    website = request.form.get('website') or ''
    orcid = request.form.get('orcid') or ''
    legal_notice = request.form.get('legalnotice') or ''
    imprint = request.form.get('imprint') or ''
    image = request.form.get('image') or ''

    editsql = """
        UPDATE  tng.config SET 
            email = NULLIF(%(email)s, ''),
            website = NULLIF(%(website)s, ''),
            orcid_id = NULLIF(%(orcid_id)s, ''),
            image = NULLIF(%(image)s, '')            
        WHERE  id = %(id)s;
    """
    try:
        g.cursor.execute('SELECT id FROM tng.config WHERE id = %(id)s',
                         {'id': int(config_id)})
        result = g.cursor.fetchone()
        if result:
            g.cursor.execute(editsql,
                             {'email': mail, 'website': website,
                              'orcid_id': orcid, 'id': config_id,
                              'image': image})
            flash(f'"{name}" updated successfully', 'success')
        else:
            flash(f'Error updating {name}', 'danger')
    except Exception as e:
        flash(f'Error updating {name}: {str(e)}', 'danger')

    update_jsonb_column('address', address, language, config_id)
    update_jsonb_column('description', description, language, config_id)
    update_jsonb_column('imprint', imprint, language, config_id)
    update_jsonb_column('legal_notice', legal_notice, language, config_id)
    update_jsonb_column('name', name, language, config_id)

    return redirect(url_for('admin') + current_tab + '/' + current_entry)


@app.route('/edit_map', methods=['POST'])
@login_required
def edit_map() -> Response:
    if current_user.group not in ['admin', 'manager']:
        abort(403)

    name = request.form.get('name')
    display_name = request.form.get('displayname')
    sortorder = request.form.get('inputorder') or ''
    tilestring = request.form.get('description')
    # current_tab = request.form.get('current_tab')
    map_id = request.form.get('map_id')

    editsql = """
        UPDATE tng.maps SET
            name = NULLIF(%(name)s, ''),
            display_name = NULLIF(%(display_name)s, ''),
            sortorder = CASE WHEN %(sortorder)s = '' THEN NULL ELSE CAST(%(
            sortorder)s AS integer) END,
            tilestring = NULLIF(%(tilestring)s, '')
        WHERE id = %(map_id)s
    """

    try:
        g.cursor.execute('SELECT id FROM tng.maps WHERE id = %(map_id)s',
                         {'map_id': map_id})
        result = g.cursor.fetchone()
        if result:
            g.cursor.execute(editsql, {
                'name': name,
                'display_name': display_name,
                'sortorder': sortorder,
                'tilestring': tilestring,
                'map_id': map_id
            })
            flash('Map updated successfully', 'map success')
        else:
            flash(f'Error updating map {map_id}', 'map danger')
    except Exception as e:
        flash(f'Error updating map {map_id}: {str(e)}', 'map danger')

    return redirect(url_for('admin'))


@app.route('/admin/add_map', methods=['POST'])
@login_required
def add_map() -> Response:
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

    # return redirect(url_for('admin'))


@app.route('/admin/delete_map/<int:map_id>')
@login_required
def delete_map(map_id: int) -> Response:
    if current_user.group not in ['admin', 'manager']:
        abort(403)

    try:
        g.cursor.execute('DELETE FROM tng.maps WHERE id = %(map_id)s',
                         {'map_id': map_id})
        flash('Map deleted successfully!', 'map success')
    except Exception as e:
        flash(f'Error deleting map: {str(e)}', 'map danger')

    return redirect(url_for('admin') + '/maps')


@app.route('/choose_indexBg', methods=['POST'])
def choose_index_bg() -> Response:
    map_id = request.form.get('mapselection')
    default_img = request.form.get('default_img')
    map_img = request.form.get('imgmap')
    greyscale = request.form.get('greyscale') == 'on'

    g.cursor.execute(
        'UPDATE tng.settings SET (index_map, index_img, img_map, greyscale) '
        '= (%s, %s, %s, %s) WHERE ID = (SELECT ID FROM tng.settings LIMIT 1)',
        (map_id, default_img, map_img, greyscale)
    )
    return redirect(url_for('admin'))


@app.route('/admin/select_entities', methods=['GET', 'POST'])
def select_entities() -> Response:
    if request.method == 'POST':
        selected_entities = request.form.getlist('selected_entities')

        selected_entities_str = json.dumps(selected_entities)

        g.cursor.execute('UPDATE tng.settings SET shown_entities = %s::JSONB',
                         (selected_entities_str,))

    return redirect(url_for('admin'))

@app.route('/admin/deselect_entities', methods=['GET', 'POST'])
def deselect_entities() -> Response:
    if request.method == 'POST':
        deselected_entities = request.form.getlist('selected_entities')

        deselected_entities_str = json.dumps(deselected_entities)

        g.cursor.execute('UPDATE tng.settings SET hidden_entities = %s::JSONB',
                         (deselected_entities_str,))

    return redirect(url_for('admin'))


@app.route('/reset')
@login_required
def reset() -> Response:
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
            VALUES ('OpenStreetMap', 'Open Street Map', 'L.tileLayer(
            "https://tile.openstreetmap.org/{z}/{x}/{y}.png", {maxZoom: 19, attribution: ''&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors''});', 1);
        
        CREATE TABLE IF NOT EXISTS tng.config
        (
            id           SERIAL PRIMARY KEY,
            name         JSONB,
            description  JSONB,
            address      JSONB,
            config_class INT,
            email        TEXT,
            orcid_id     TEXT,
            image        TEXT,
            website      TEXT,
            legal_notice JSONB,
            imprint      JSONB
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
            name        JSONB,
            name_inv    JSONB,
            description JSONB,
            domain      INT,
            range       INT
        );
        
        ALTER TABLE tng.config
            ADD CONSTRAINT config_config_classes_fk FOREIGN KEY (
            config_class) REFERENCES tng.config_classes (id);
        ALTER TABLE tng.links
            ADD CONSTRAINT links_config_properties_fk FOREIGN KEY (property) 
            REFERENCES tng.config_properties (id);
        ALTER TABLE tng.links
            ADD CONSTRAINT links_config_fk_domain FOREIGN KEY (domain_id) 
            REFERENCES tng.config (id);
        ALTER TABLE tng.links
            ADD CONSTRAINT links_config_fk_range FOREIGN KEY (range_id) 
            REFERENCES tng.config (id);
        ALTER TABLE tng.links
            ADD CONSTRAINT links_config_fk_role FOREIGN KEY (attribute) 
            REFERENCES tng.config (id);
        
        CREATE OR REPLACE FUNCTION tng.delete_links_on_config_delete()
            RETURNS trigger
            LANGUAGE plpgsql
        AS
        $function$
        BEGIN
            DELETE FROM tng.links WHERE domain_id = OLD.id OR range_id = 
            OLD.id;
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
        
        INSERT INTO tng.config_properties (name, name_inv, domain, range)
        VALUES ('{"de": "hat Mitglied", "en": "has member"}'::jsonb, '{"de": "ist Mitglied von", "en": "is member of"}'::jsonb, 
                (SELECT id FROM tng.config_classes WHERE name = 'project'), 
                (SELECT id FROM tng.config_classes WHERE name = 'person'));
        
        INSERT INTO tng.config_properties (name, name_inv, domain, range)
        VALUES ('{"de": "hat Zugehörigkeit", "en": "has affiliation"}'::jsonb, '{"de": "ist Zugehörigkeit von", "en": "is affiliation of"}'::jsonb, (SELECT id FROM tng.config_classes WHERE name = 'person'), (SELECT id FROM tng.config_classes WHERE name = 'institution'));
        
        INSERT INTO tng.config_properties (name, name_inv, domain, range)
        VALUES ('{"de": "hat Kernmitglied", "en": "has core member"}'::jsonb, '{"de": "ist Kernmitglied von", "en": "is core member of"}'::jsonb, 
                (SELECT id FROM tng.config_classes WHERE name = 
                'main-project'), (SELECT id FROM tng.config_classes WHERE name = 'person'));
        
        INSERT INTO tng.config_properties (name, name_inv, domain, range)
        VALUES ('{"de": "hat Kerninstitution", "en": "has core institution"}'::jsonb, '{"de": "ist Kerninstitution von", "en": "is core institution of"}'::jsonb, 
                (SELECT id FROM tng.config_classes WHERE name = 
                'main-project'), (SELECT id FROM tng.config_classes WHERE 
                name = 'institution'));

        INSERT INTO tng.config_properties (name, name_inv, domain, range)
        VALUES ('{"de": "hat Institution", "en": "has institution"}'::jsonb, '{"de": "ist Institution von", "en": "is institution of"}'::jsonb, 
                (SELECT id FROM tng.config_classes WHERE name = 'project'), 
                (SELECT id FROM tng.config_classes WHERE name = 
                'institution'));
        
        INSERT INTO tng.config (name, config_class, description, address, 
        email, website)
        VALUES ('{"de": "Hauptprojekt", "en": "Main Project"}'::jsonb, 
        (SELECT id from tng.config_classes WHERE name = 'main-project'), 
        NULL, NULL, NULL, NULL);
        
        INSERT INTO tng.config (name, config_class, description, address, 
        email, website)
        VALUES ('{"de": "Stefan Eichert", "en": "Stefan Eichert"}'::jsonb, 
        (SELECT id from tng.config_classes WHERE name = 'person'), NULL, 
        NULL, NULL, NULL);
        
        INSERT INTO tng.config (name, config_class, description, address, 
        email, website)
        VALUES ('{"de": "Lisa Aldrian", "en": "Lisa Aldrian"}'::jsonb, 
        (SELECT id from tng.config_classes WHERE name = 'person'), NULL, 
        NULL, NULL, NULL);
        
        INSERT INTO tng.config (name, config_class, description, address, 
        email, website)
        VALUES ('{"de": "David Ruß", "en": "David Ruß"}'::jsonb, (SELECT id 
        from tng.config_classes WHERE name = 'person'), NULL, NULL, NULL, 
        NULL);
        
        INSERT INTO tng.config (name, config_class, description, address, 
        email, website)
        VALUES ('{"de": "Projektleitung", "en": "Principal Investigator"}'::jsonb, (SELECT id from tng.config_classes WHERE name = 'role'), NULL, NULL, NULL, NULL);
        
        INSERT INTO tng.config (name, config_class, description, address, 
        email, website)
        VALUES ('{"de": "Hauptkoordinator", "en": "Main Coordinator"}'::jsonb, (SELECT id from tng.config_classes WHERE name = 'role'), NULL, NULL, NULL, NULL);
        
        INSERT INTO tng.config (name, config_class, description, address, 
        email, website)
        VALUES ('{"de": "Forscher", "en": "Researcher"}'::jsonb, (SELECT id 
        from tng.config_classes WHERE name = 'role'), NULL, NULL, NULL, NULL);
        
        INSERT INTO tng.config (name, config_class, description, address, 
        email, website)
        VALUES ('{"de": "Softwareentwickler", "en": "Software Developer"}'::jsonb, (SELECT id from tng.config_classes WHERE name = 
        'role'), NULL, NULL, NULL, NULL);
        
        INSERT INTO tng.config (name, config_class, description, address, 
        email, website)
        VALUES ('{"de": "Design & Programmierung", "en": "Design & Programming"}'::jsonb, (SELECT id from tng.config_classes WHERE name 
        = 'role'), NULL, NULL, NULL, NULL);
        
        INSERT INTO tng.config (name, config_class, description, address, 
        email, website)
        VALUES ('{"de": "Archäologe", "en": "Archaeologist"}'::jsonb, 
        (SELECT id from tng.config_classes WHERE name = 'role'), NULL, NULL, 
        NULL, NULL);
        
        INSERT INTO tng.config (name, config_class, description, address, 
        email, website)
        VALUES ('{"de": "Anthropologe", "en": "Anthropologist"}'::jsonb, 
        (SELECT id from tng.config_classes WHERE name = 'role'), NULL, NULL, 
        NULL, NULL);
        
        INSERT INTO tng.config (name, config_class, description, address, 
        email, website)
        VALUES ('{"de": "Datenaufnahme", "en": "Data Acquisition"}'::jsonb, 
        (SELECT id from tng.config_classes WHERE name = 'role'), NULL, NULL, 
        NULL, NULL);
        
        INSERT INTO tng.config (name, config_class, description, address, 
        email, website)
        VALUES ('{"de": "Historiker", "en": "Historian"}'::jsonb, (SELECT id 
        from tng.config_classes WHERE name = 'role'), NULL, NULL, NULL, NULL);
        
        INSERT INTO tng.config (name, config_class, description, address, 
        email, website)
        VALUES ('{"de": "Sponsor", "en": "Sponsor"}'::jsonb, (SELECT id from 
        tng.config_classes WHERE name = 'role'), NULL, NULL, 
        'https://example.example', NULL);
        
        INSERT INTO tng.config (name, config_class, description, address, 
        email, website)
        VALUES ('{"de": "Partner", "en": "Partner"}'::jsonb, (SELECT id from 
        tng.config_classes WHERE name = 'role'), NULL, NULL, 
        'https://example.example', NULL);
        
        INSERT INTO tng.config (name, config_class, description, address, 
        email, website)
        VALUES ('{"de": "THANADOS", "en": "THANADOS"}'::jsonb, (SELECT id 
        from tng.config_classes WHERE name = 'project'), NULL, NULL, NULL, 
        NULL);
        
        INSERT INTO tng.config (name, config_class, description, address, 
        email, website)
        VALUES ('{"de": "RELIC", "en": "RELIC"}'::jsonb, (SELECT id from 
        tng.config_classes WHERE name = 'project'), NULL, NULL, NULL, NULL);
        
        INSERT INTO tng.config (name, config_class, description, address, 
        email, website)
        VALUES ('{"de": "REPLICO", "en": "REPLICO"}'::jsonb, (SELECT id from 
        tng.config_classes WHERE name = 'project'), NULL, NULL, NULL, NULL);
        
        INSERT INTO tng.config (name, config_class, description, address, 
        email, website)
        VALUES ('{"de": "NHM", "en": "NHM"}'::jsonb, (SELECT id from tng.config_classes WHERE name = 'institution'), NULL, NULL, NULL, 
        NULL);
        
        INSERT INTO tng.config (name, config_class, description, address, 
        email, website)
        VALUES ('{"de": "Universität Wien", "en": "University of Vienna"}'::jsonb, (SELECT id from tng.config_classes WHERE name = 
        'institution'), NULL, NULL, NULL, NULL);
        
        INSERT INTO tng.config (name, config_class, description, address, 
        email, website)
        VALUES ('{"en": "Austrian Centre for Digital Humanities & Cultural Heritage"}'::jsonb, (SELECT id from tng.config_classes WHERE name = 
        'institution'), NULL, NULL, NULL, NULL);

        
        CREATE TABLE IF NOT EXISTS tng.settings
        (
            id        SERIAL PRIMARY KEY,
            index_img TEXT,
            index_map INT,
            img_map   TEXT,
            greyscale   BOOLEAN,
            shown_entities  JSONB, --classes
            shown_types JSONB, --types
            hidden_entities  JSONB, --classes
            hidden_types JSONB, --types
            shown_ids JSONB, --ids
            hidden_ids JSONB --ids
        );

        INSERT INTO tng.settings (index_img, index_map, img_map, greyscale, 
        shown_entities)
        VALUES ('/static/images/index_map_bg/Blank_map_of_Europe_central_network.png', 1, 'image', TRUE, '[]'::JSONB)
        
        
        create function tng.getdates(first timestamp without time zone, last timestamp without time zone, comment text) returns text
            language plpgsql
        as
        $$
        DECLARE
            return_date TEXT;
        BEGIN
            CASE
                WHEN comment LIKE '-%' THEN
                    -- Use the comment as a negative year with leading zeros
                    SELECT TO_CHAR(comment::INTEGER, 'FM000000000') INTO return_date;
                ELSE
                    -- Use the date logic
                    SELECT TO_CHAR(LEAST(first, last), 'FM00000YYYY-MM-DD') INTO return_date;
                CASE WHEN EXTRACT(YEAR FROM (LEAST(first, last)::DATE)) < 1 THEN SELECT '-' || return_date INTO return_date; ELSE NULL; END CASE;
            END CASE;
        
            RETURN return_date;
        END;
        $$;
        
    ''')

    return redirect(url_for('admin'))


# @app.route('/sortlinks', methods=['POST'])
# def sort_links() -> Response:
#     @login_required
#     def reset_():
#         if current_user.group not in ['admin', 'manager']:
#             abort(403)
#
#     data = request.get_json()
#     criteria = data['criteria']
#     table = data['table']
#
#     for row in criteria:
#         g.cursor.execute(
#             f'UPDATE tng.{table} SET sortorder = %(order)s  WHERE id = %(id)s',
#             {'id': row['id'], 'order': row['order'], 'table': table})
#     return jsonify({'status': 'ok'})
