from flask import Response, g, jsonify, render_template, request

from histarchexplorer import app
from histarchexplorer.utils.view_util import render_page_template


@app.route('/search', methods=['GET', 'POST'])
def search() -> str:
    """Render the advanced search page and process search requests.

    Supports custom text queries, system class filtering, and category
    restrictions.
    """
    search_service = g.search_service

    results = []
    query = ''
    category = 'all'
    system_classes = []

    if request.method == 'POST':
        query = request.form.get('query', '').strip()
        category = request.form.get('category', 'all').strip()
        system_classes = request.form.getlist('system_class[]')

        results = search_service.perform_search(
            query,
            category,
            system_classes)

    return render_page_template(
        'search',
        results=results,
        query=query,
        category=category,
        system_classes=system_classes)


@app.route('/search_live')
def search_live() -> Response:
    """Perform real-time live search and return the results as JSON.

    Used by autocomplete or quick search bars in the navigation layout.

    Returns:
        Response: JSON list of autocomplete results as returned by
            `SearchService.perform_live_search`.
    """
    search_service = g.search_service

    query = request.args.get('q', '').strip()
    system_classes = request.args.getlist('system_class')

    results = search_service.perform_live_search(query, system_classes)

    return jsonify(results)



