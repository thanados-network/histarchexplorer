from typing import Optional

from flask import redirect, render_template, request, session
from werkzeug import Response
from flask import Response, redirect, render_template, request, session, g

from histarchexplorer import app
from histarchexplorer.utils import cerberos


@app.route('/')
def index():
    g.cursor.execute('SELECT index_img, index_map, img_map, greyscale FROM tng.settings LIMIT 1')
    data = g.cursor.fetchone()

    g.cursor.execute(f'SELECT tilestring FROM tng.maps WHERE id={data.index_map}')
    map = g.cursor.fetchone()

    view_classes = cerberos.gatekeeper()



    return render_template('index.html', map=map.tilestring, img=data.index_img, img_map=data.img_map, greyscale=data.greyscale, view_classes=view_classes, viewcount=len(view_classes.keys()))




@app.route('/search')
def search() -> str:
    return render_template('search.html')


@app.route('/language=<language>')
def set_language(language: Optional[str] = None) -> Response:
    session['language'] = language
    return redirect(request.referrer)
