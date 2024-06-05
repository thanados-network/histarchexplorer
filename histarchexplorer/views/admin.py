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

    return render_template("/admin.html", config_data=config_data, tabs=tabs, activetab=tab, activeentry=entry)

@app.route('/admin/add_entry', methods=['POST'])
@login_required
def add_entry():
    if current_user.group not in ['admin', 'manager']:
        abort(403)

    original_tab_label = request.form.get(
        'tab')  # Get the tab label from the form with the 'nav-' prefix - to determine the config class of the entry being added based on the tab from which the form was submitted
    print("Received tab label:", original_tab_label)
    tab_label = original_tab_label.replace('nav-', '')  # Remove 'nav-' prefix from the tab label

    current_tab = request.form.get('current_tab')
    name = request.form.get('name')
    description = request.form.get('description')
    address = request.form.get('address')
    mail = request.form.get('mail')
    website = request.form.get('website')
    orcid = request.form.get('orcid')

    # Dictionary to classify the type of entry being added
    config_class_map = {
        'projects': 1, #option for config_class=2 project vs 1=main_project?
        'persons': 3,
        'institutions': 5,
        'attributes': 4
    }

    new_entry_id = None  # Initialize new_entry_id to None

    try:
        # Get the config class corresponding to the tab label
        tab_config_class = config_class_map.get(tab_label)
        #if tab_config_class is None:
        #   raise ValueError('Invalid tab label')

        # Insert the entry into the database
        g.cursor.execute('''
                   INSERT INTO tng.config (name, description, address, email, website, orcid_id, config_class)
                   VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id
               ''', (name, description, address, mail, website, orcid, tab_config_class))
        new_entry_id = g.cursor.fetchone()[0]
        flash('Entry added successfully!', 'success')
    except Exception as e:
        g.db.rollback()  # reverts changes during transaction if any error ocurrs
        flash(f'Error adding entry: {str(e)}', 'danger')

    return redirect(f'/admin/{current_tab}/{current_tab}{new_entry_id}')

@app.route('/admin/delete_entry/<id>/<tab>')
@login_required
def delete_entry(tab: Optional[str] = None, id: Optional[int] = None) -> str:
    if current_user.group not in ['admin', 'manager']:
        abort(403)


    g.cursor.execute('DELETE FROM tng.config WHERE id = %(id)s', {'id':int(id)})
    return redirect('/admin/'+ tab)

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
            g.cursor.execute(editsql, {'description': description, 'name': name, 'address': address, 'email': mail, 'website': website, 'orcid_id': orcid, 'id': config_id})
            flash(f'"{name}" updated successfully', 'success')
        else:
            flash(f'Error updating {name}', 'danger')
    except Exception as e:
        flash(f'Error updating {name}: {str(e)}', 'danger')

    return redirect(url_for('admin') + current_tab + '/' + current_entry)
