from typing import Optional

from flask import redirect, render_template, request, session
from werkzeug import Response
from flask import Response, redirect, render_template, request, session, g

from histarchexplorer import app


@app.route('/')
def index() -> str:
    default_image = '/../static/images/index_map_bg/Blank_map_of_Europe_central_network.png'
    return render_template('index.html', default_image=default_image)


@app.route('/entities')
def entities() -> str:
    return render_template('entities.html')


@app.route('/search')
def search() -> str:
    return render_template('search.html')

@app.route('/language=<language>')
def set_language(language: Optional[str] = None) -> Response:
    session['language'] = language
    return redirect(request.referrer)
