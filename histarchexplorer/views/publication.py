from histarchexplorer import app
from histarchexplorer.utils.view_util import render_page_template


@app.route('/publications')
def publications() -> str:
    return render_page_template('publications')
