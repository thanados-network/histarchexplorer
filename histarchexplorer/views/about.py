from flask import render_template, g

from histarchexplorer import app


@app.route('/about')
def about() -> str:
    sql = """
        SELECT name, description FROM tng.config WHERE config_class = '1'
    """

    g.cursor.execute(sql)
    result = g.cursor.fetchone()
    project = result.name
    description = result.description
    return render_template('about.html', project=project, description=description)


