from histarchexplorer import app
from histarchexplorer.utils.view_util import render_page_template


@app.route('/outcome')
def outcome() -> str:
    """Render the project outcomes or publication results page.

    Compiles the default layout template for project findings.
    """
    return render_page_template('outcome')
