from typing import Optional

from flask import render_template, abort, g, request, redirect, url_for, flash
from flask_login import (
    current_user, login_required)

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
            'id': 'nav-project-tab',
            'label': 'projects',
            'target': 'nav-project',
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


@app.route('/add_description', methods=['POST', 'GET'])
@login_required
def add_description():
    if current_user.group not in ['admin', 'manager']:
        abort(403)

    description = request.form.get('description')
    config_id = request.form.get('config_id')
    current_tab = request.form.get('current_tab')
    current_entry = request.form.get('current_entry')
    project_name = request.form.get('projectName')
    address = request.form.get('address')
    mail = request.form.get('mail')
    website = request.form.get('website')
    orcid = request.form.get('orcid')

    # Initialize a dictionary to hold status messages
    status_messages = {}

    # Define a function to update a field and store the result in status_messages
    def update_field(field_name, field_value, column_name):
        if field_value:
            try:
                g.cursor.execute(f'UPDATE tng.config SET {column_name} = %s WHERE id = %s', (field_value, config_id))
                g.db.commit()
                status_messages[field_name] = ('success', f'{field_name.capitalize()} updated successfully!')
            except Exception as e:
                g.db.rollback()
                status_messages[field_name] = ('danger', f'Error updating {field_name}: {str(e)}')

    # Update each field and store the corresponding status message
    update_field('description', description, 'description')
    update_field('project name', project_name, 'name')
    update_field('address', address, 'address')
    update_field('email', mail, 'email')
    update_field('website', website, 'website')
    update_field('orcid-id', orcid, 'orcid')

    # Flash each status message
    for field, (category, message) in status_messages.items():
        flash(message, category)

    return redirect('/admin/' + current_tab + '/' + current_entry)
