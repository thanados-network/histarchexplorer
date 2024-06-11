from typing import Optional

from flask import render_template, abort, g, request, redirect, url_for, flash, jsonify
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

    g.cursor.execute('SELECT * FROM tng.config_classes')
    config_classes = g.cursor.fetchall()

    projects = []
    persons = []
    institutions = []
    roles = []
    for row in config_classes:
        if row.name in ['project', 'main_project']:
            projects.append(row.id)
        if row.name in ['person']:
            persons.append(row.id)
        if row.name in ['institution']:
            institutions.append(row.id)
        if row.name in ['role']:
            roles.append(row.id)

    tabs = [
        {
            'id': 'nav-projects-tab',
            'label': 'projects',
            'target': 'nav-projects',
            'filter': projects
        },
        {
            'id': 'nav-persons-tab',
            'label': 'persons',
            'target': 'nav-persons',
            'filter': persons
        },
        {
            'id': 'nav-institutions-tab',
            'label': 'institutions',
            'target': 'nav-institutions',
            'filter': institutions
        },
        {
            'id': 'nav-attributes-tab',
            'label': 'attributes',
            'target': 'nav-attributes',
            'filter': roles
        }
    ]

    # Fetch linked entries
    g.cursor.execute("""
        SELECT 
            l.id AS link_id, 
            s.name AS start_name, 
            e.name AS end_name, 
            cp.name AS config_property, 
            cp.name_inv AS config_property_inv, 
            r.name AS role
        FROM tng.links l
        JOIN tng.config s ON l.domain_id = s.id
        JOIN tng.config e ON l.range_id = e.id
        JOIN tng.config_properties cp ON l.property = cp.id
        LEFT JOIN tng.config r ON l.attribute = r.id
    """)
    links_data = g.cursor.fetchall()

    return render_template("/admin.html", config_data=config_data, tabs=tabs, activetab=tab, activeentry=entry,
                           links_data=links_data)


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

    # Dictionary to classify the type of entry being added
    config_class_map = {
        'projects': 1,  # option for config_class=2 project vs 1=main_project?
        'persons': 3,
        'institutions': 5,
        'attributes': 4
    }

    try:
        # Get the config class corresponding to the tab label
        tab_config_class = config_class_map.get(category)

        # Insert the entry into the database
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

    g.cursor.execute('DELETE FROM tng.config WHERE id = %(id)s', {'id': int(id)})
    flash('Entry deleted successfully!', 'success')
    return redirect(url_for('admin') + tab)

#Delete Links
@app.route('/admin/delete_link/<link_id>/<tab>')
@login_required
def delete_link(link_id: Optional[int] = None, tab: Optional[str] = None) -> str:
    if current_user.group not in ['admin', 'manager']:
        abort(403)

    g.cursor.execute('DELETE FROM tng.links WHERE id = %(link_id)s', {'link_id': int(link_id)})
    flash('Link deleted successfully!', 'success')
    return redirect(url_for('admin') + tab) #irgendwie in den entry und net in den tab


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

    editsql = """
        UPDATE  tng.config SET 
            description = NULLIF(%(description)s, ''),
            name = NULLIF(%(name)s, ''),
            address = NULLIF(%(address)s, ''),
            email = NULLIF(%(email)s, ''),
            website = NULLIF(%(website)s, ''),
            orcid_id = NULLIF(%(orcid_id)s, '')
        WHERE  id = %(id)s
    """
    try:
        g.cursor.execute('SELECT id FROM tng.config WHERE id = %(id)s', {'id': int(config_id)})
        result = g.cursor.fetchone()
        if result:
            g.cursor.execute(editsql, {'description': description, 'name': name, 'address': address, 'email': mail,
                                       'website': website, 'orcid_id': orcid, 'id': config_id})
            flash(f'"{name}" updated successfully', 'success')
        else:
            flash(f'Error updating {name}', 'danger')
    except Exception as e:
        flash(f'Error updating {name}: {str(e)}', 'danger')

    return redirect(url_for('admin') + current_tab + '/' + current_entry)
