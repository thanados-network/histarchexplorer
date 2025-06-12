import requests
from flask import current_app

def search_entities(query: str, category: str, system_classes: list):
    results = []

    if not system_classes:
        if category in current_app.config['VIEW_CLASSES']:
            system_class = current_app.config['VIEW_CLASSES'][category][0]
        else:
            system_class = "all"
        url = f"{current_app.config['API_URL']}api/search/{system_class}/{query}"
        results = fetch_results(url)
    else:
        for sc in system_classes:
            url = f"{current_app.config['API_URL']}search/{sc}/{query}"
            results.extend(fetch_results(url))

    return results

def fetch_entity_detail(entity_id: int):
    url = f"{current_app.config['API_URL']}entity/{entity_id}"
    data = fetch_results(url)
    return data['features'][0] if 'features' in data and data['features'] else {}

def search_live_results(query: str, system_classes: list):
    results = []
    if not system_classes:
        system_classes = ['all']

    for sc in system_classes:
        url = f"{current_app.config['API_URL']}search/{sc}/{query}"
        results.extend(fetch_results(url))

    return results

def fetch_results(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("results", []) if isinstance(data.get("results"), list) else data
    except Exception:
        return []
