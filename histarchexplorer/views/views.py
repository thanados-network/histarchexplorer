from typing import Optional

from flask import Response, redirect, render_template, request, session, g

from runserver import app


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/entities')
def entities():
    return render_template('entities.html')


@app.route('/search')
def search():
    return render_template('search.html')


@app.route('/about')
def about():
    sql = """
        SELECT name, description FROM tng.config WHERE config_class = '1'
    """

    g.cursor.execute(sql)
    result = g.cursor.fetchone()
    project = result.name
    description = result.description
    return render_template('about.html', project=project, description=description)


@app.route('/language=<language>')
def set_language(language: Optional[str] = None) -> Response:
    session['language'] = language
    return redirect(request.referrer)


