from flask import render_template

from runserver import app


@app.route('/')
def index():
    return render_template('layout.html')


@app.route('/sites')
def sites():
    return render_template('sites.html')


@app.route('/about')
def about():
    return render_template('about.html')
