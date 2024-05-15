from flask import render_template, abort, g
from flask_login import (
    current_user, login_required)

from histarchexplorer import app


@app.route('/admin')
@login_required
def admin() -> str:
    if current_user.group not in ['admin', 'manager']:
        abort(403)

    g.cursor.execute('SELECT* FROM tng.config')
    config_data = g.cursor.fetchall()

    g.cursor.execute('SELECT* FROM tng.config_classes')
    config_classes = g.cursor.fetchall()

    projects = [] #array/list
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
            'filter': projects  # Assuming projects is defined in your Flask route function
        },
        {
            'id': 'nav-persons-tab',
            'label': 'persons',
            'target': 'nav-persons',
            'filter': persons  # Assuming persons is defined in your Flask route function
        },
        {
            'id': 'nav-institutions-tab',
            'label': 'institutions',
            'target': 'nav-institutions',
            'filter': institutions  # Assuming institutions is defined in your Flask route function
        },
        {
            'id': 'nav-attributes-tab',
            'label': 'attributes',
            'target': 'nav-attributes',
            'filter': roles  # Assuming roles is defined in your Flask route function
        }
    ]

    return render_template("/admin.html", config_data=config_data, tabs=tabs)
