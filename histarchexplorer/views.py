from flask import render_template

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
    return render_template('about.html')
