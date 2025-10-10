from histarchexplorer import app
from flask import render_template, current_app
import requests

from histarchexplorer.api.presentation_view import PresentationView
from histarchexplorer.utils.view_util import get_cite_button

TYPE_TREE_API_URL = "https://thanados.openatlas.eu/api/0.4/type_tree/"

@app.route("/vocabulary")
def vocabulary():
    # Strict: require these to exist in config (default.py)
    vocab_tabs = current_app.config["VOCAB_TREES"]

    return render_template(
        "vocabulary.html",
        vocab_tabs=vocab_tabs,
        type_tree_api_url=TYPE_TREE_API_URL,
    )


@app.route("/vocabulary/<int:type_id>")
def vocabulary_detail(type_id: int):
    entity = PresentationView.from_api(type, type_id)
    res = requests.get(TYPE_TREE_API_URL)

    res.raise_for_status()
    type_tree = res.json().get("typeTree", {})

    type_ = type_tree.get(str(type_id))
    if not type_:
        return f"Type with ID {type_id} not found.", 404

    parents = [type_tree.get(str(pid)) for pid in type_.get("root", [])]
    children = [type_tree.get(str(cid)) for cid in type_.get("subs", [])]

    exact_res = requests.get(f"https://thanados.openatlas.eu/api/0.4/type_entities/{type_id}")
    exact_res.raise_for_status()
    exact_entities = exact_res.json().get("features", [])

    all_res = requests.get(f"https://thanados.openatlas.eu/api/0.4/type_entities_all/{type_id}")
    all_res.raise_for_status()
    raw_results = all_res.json().get("results", [])
    all_entities = [f for g in raw_results for f in g.get("features", [])]
    subcategory_entities = [e for e in all_entities if e not in exact_entities]

    return render_template(
        "vocabulary_detail.html",
        entity=entity,
        type=type_,
        parents=parents,
        children=children,
        exact_entities=exact_entities,
        subcategory_entities=subcategory_entities,
        cite_button=get_cite_button(entity),
    )

