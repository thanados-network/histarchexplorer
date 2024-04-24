from typing import Optional

from flask import Response, redirect, render_template, request, session

from histarchexplorer import app
from histarchexplorer.model.entity import Entity


@app.route('/')
def index() -> str:
    return render_template('index.html')


@app.route('/entities')
def entities() -> str:
    return render_template('entities.html')


@app.route('/search')
def search() -> str:
    return render_template('search.html')


@app.route('/about')
def about() -> str:
    return render_template('about.html')


@app.route('/test')
def test() -> str:
    return render_template('api.html')


@app.route('/api/entity/<int:id_>')
def test_entity(id_: int) -> str:
    entity = Entity.get_entity(id_)
    return render_template('entity.html', entity=entity)


@app.route('/language=<language>')
def set_language(language: Optional[str] = None) -> Response:
    session['language'] = language
    return redirect(request.referrer)
