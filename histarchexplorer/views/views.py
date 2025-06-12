from typing import Optional

from flask import jsonify, redirect, session
from werkzeug import Response

from histarchexplorer import app
from histarchexplorer.database.map import get_map_tilestring
from histarchexplorer.database.settings import get_map_settings
from histarchexplorer.utils.cerberos import get_view_class_count


@app.route('/')
def index() -> str:
    map_data = get_map_settings()
    map_ = get_map_tilestring(map_data)

    view_classes = get_view_class_count()

    return render_template(
        'index.html',
        map=map_.tilestring,
        map_data=map_data,
        view_classes=view_classes)


import requests
from flask import render_template, request


@app.route('/search', methods=['GET', 'POST'])
def search():
    results = []
    query = ''
    category = 'all'
    system_classes = []

    if request.method == 'POST':
        query = request.form.get('query', '').strip()
        category = request.form.get('category', 'all').strip()
        system_classes = request.form.getlist('system_class[]')

        if not system_classes:
            if category in app.config['VIEW_CLASSES']:
                system_class = app.config['VIEW_CLASSES'][category][0]
            else:
                system_class = "all"
            url = f"https://thanados.openatlas.eu/api/search/{system_class}/{query}"
            print(f"📡 Requesting: {url}")
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                data = response.json()
                results = data.get("results", []) if isinstance(data.get("results", []), list) else []
                print(f"✅ Found {len(results)} result(s)")
            except Exception as e:
                print(f"❌ Search failed: {e}")
        else:
            for sc in system_classes:
                url = f"https://thanados.openatlas.eu/api/search/{sc}/{query}"
                print(f"📡 Requesting: {url}")
                try:
                    response = requests.get(url, timeout=10)
                    response.raise_for_status()
                    data = response.json()
                    if isinstance(data.get("results"), list):
                        results.extend(data["results"])
                except Exception as e:
                    print(f"❌ Search failed for {sc}: {e}")

    return render_template(
        'search.html',
        results=results,
        query=query,
        category=category,
        system_classes=system_classes
    )


@app.route('/search_result/<int:entity_id>')
def search_result_detail(entity_id: int):
    url = f"https://thanados.openatlas.eu/api/entity/{entity_id}"
    print(f"📡 Fetching entity from: {url}")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        entity = data['features'][0]
    except Exception as e:
        print(f"❌ Failed to fetch detail: {e}")
        return render_template("not_found.html", id=entity_id), 404

    return render_template('search_detail.html', entity=entity)


@app.route('/language=<language>')
def set_language(language: Optional[str] = None) -> Response:
    session['language'] = language
    return redirect(request.referrer)




@app.route('/search_live')
def search_live():
    query = request.args.get('q', '').strip()
    system_classes = request.args.getlist('system_class')  # multiple values like system_class=place&system_class=artifact

    if len(query) < 3:
        return jsonify([])

    if not system_classes:
        system_classes = ['all']

    results = []

    for system_class in system_classes:
        api_url = f"https://thanados.openatlas.eu/api/search/{system_class}/{query}"
        print(f"📡 LIVE Requesting: {api_url}")
        try:
            response = requests.get(api_url, timeout=10)
            response.raise_for_status()
            data = response.json()
            class_results = data.get("results", [])
            if isinstance(class_results, list):
                results.extend(class_results)
        except Exception as e:
            print(f"❌ Live search error for {system_class}: {e}")

    print(f"✅ LIVE Found {len(results)} result(s) total")
    return jsonify(results)

