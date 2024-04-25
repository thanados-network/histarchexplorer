from typing import Optional

from flask import Response, redirect, render_template, request, session

from runserver import app


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/entities')
def entities():
    return render_template('entities.html', current_page='entities')


@app.route('/search')
def search():
    return render_template('search.html', current_page='search')


@app.route('/about')
def about():
    return render_template('about.html', current_page='about')


@app.route('/language=<language>')
def set_language(language: Optional[str] = None) -> Response:
    session['language'] = language
    return redirect(request.referrer)
