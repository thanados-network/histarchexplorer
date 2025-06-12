from flask import render_template, request, jsonify
from histarchexplorer import app
from histarchexplorer.services import search_service


@app.route('/search', methods=['GET', 'POST'])
def search():
    results, query, category, system_classes = [], '', 'all', []

    if request.method == 'POST':
        query = request.form.get('query', '').strip()
        category = request.form.get('category', 'all').strip()
        system_classes = request.form.getlist('system_class[]')
        results = search_service.search_entities(query, category, system_classes)

    return render_template(
        'search.html',
        results=results,
        query=query,
        category=category,
        system_classes=system_classes
    )


@app.route('/search_result/<int:entity_id>')
def search_result_detail(entity_id: int):
    entity = search_service.fetch_entity_detail(entity_id)
    return render_template('search_detail.html', entity=entity)


@app.route('/search_live')
def search_live():
    query = request.args.get('q', '').strip()
    system_classes = request.args.getlist('system_class')
    if len(query) < 3:
        return jsonify([])

    results = search_service.search_live_results(query, system_classes)
    return jsonify(results)
