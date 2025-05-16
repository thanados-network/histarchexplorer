from flask import render_template

from histarchexplorer import app
from histarchexplorer.utils import cerberos


@app.route('/entities')
def entities() -> str:
    return render_template(
        'entities.html',
        view_classes=cerberos.get_view_class_count())
