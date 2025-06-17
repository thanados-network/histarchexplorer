from flask import jsonify, render_template, request, current_app
from histarchexplorer import app


@app.route('/search', methods=['GET', 'POST'])
def search():
    """
    Handles the main search page, displaying results from the search service.
    """
    search_service = current_app.search_service

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

    return render_template(
        'search.html',
        results=results,
        query=query,
        category=category,
        system_classes=system_classes)


# @app.route('/search_result/<int:entity_id>')
# def search_result_detail(entity_id: int):
#     """
#     Displays detailed information for a specific search result entity.
#     """
#     search_service = current_app.search_service
#     entity = search_service.get_entity_detail(entity_id)
#
#     if entity is None:
#         current_app.logger.warning(
#             f"Entity with ID {entity_id} not found or error fetching.")
#         return render_template('error.html', message="Entity not found."), 404
#
#     return render_template('search_detail.html', entity=entity)


@app.route('/search_live')
def search_live():
    """
    Provides live search results for autocomplete features.
    """
    search_service = current_app.search_service

    query = request.args.get('q', '').strip()
    system_classes = request.args.getlist('system_class')

    results = search_service.perform_live_search(query, system_classes)

    return jsonify(results)
