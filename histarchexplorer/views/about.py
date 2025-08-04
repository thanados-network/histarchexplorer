from flask import g, render_template

from histarchexplorer import app
from histarchexplorer.services.config import ConfigEntity


@app.route('/about')
def about() -> str:
    grouped = ConfigEntity.group_by_class_name(g.config_entities)
    return render_template(
        'about.html',
        project=grouped.get('main-project', [None])[0],
        sub_projects=grouped.get('project', []),
        institutions=grouped.get('institution', []),
        persons=grouped.get('person', []))
