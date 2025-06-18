from flask import render_template

from histarchexplorer import app
from histarchexplorer.services.about import Institution, Person, Project


@app.route('/about')
def about() -> str:
    project = None
    sub_projects = []
    for p in Project.get_all_localized():
        if p.main_project:
            project = p
            continue
        sub_projects.append(p)

    return render_template(
        'about.html',
        project=project,
        sub_projects=sub_projects,
        institutions=Institution.get_all_localized(),
        persons=Person.get_all_localized())
