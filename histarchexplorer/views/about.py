from typing import Optional

from flask import g, render_template

from histarchexplorer import app
from histarchexplorer.models.config import ConfigEntity


@app.route('/about')
@app.route('/about/<int:id_>')
def about(id_: Optional[int] = None):
    grouped = ConfigEntity.group_by_class_name(g.config_entities)
    config_entities_mapped = {e.id: e for e in g.config_entities}
    return render_template(
        "about.html",
        active=config_entities_mapped[id_] if id_ else grouped.get('main-project', [None])[0],
        main_project=grouped.get('main-project', [None])[0],
        sub_projects=grouped.get('project', []),
        config_entities_mapped=config_entities_mapped)
