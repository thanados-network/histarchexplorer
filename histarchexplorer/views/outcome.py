from histarchexplorer import app
from histarchexplorer.utils.view_util import render_page_template


@app.route('/outcome')
def outcome() -> str:
    return render_page_template('outcome')
