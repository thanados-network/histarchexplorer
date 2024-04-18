from flask import Flask, render_template

app = Flask(__name__, instance_relative_config=True)

app.config.from_pyfile('production.py')


@app.route('/')
def index():
    return render_template('layout.html')


@app.route('/sites')
def sites():
    return render_template('sites.html')


@app.route('/about')
def about():
    return render_template('about.html')


if __name__ == '__main__':
    app.run()
