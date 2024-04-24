from flask import render_template

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