import datetime
from typing import Any

from flask import g, render_template, url_for
from flask_babel import lazy_gettext as _

from histarchexplorer import app
from histarchexplorer.api.presentation_view import PresentationView

_('entities')
_('search')
_('about')
_('test')


@app.context_processor
def inject_menu() -> dict[str, Any]:
    navbar = [
        {'entities': _('browse/select/find all entities')},
        {'search': _('detailed search')},
        {'about': _('about the project')}]
    return {'navbar': navbar}


def find_children_by_id(data, target_id):
    result = []

    def collect_descendants(children, depth=1):
        for child in children:
            prefix = '-' * depth
            name = child['name']
            result.append({'id': child['id'], 'name': f"{prefix}{name}"})
            if 'children' in child and child['children']:
                collect_descendants(child['children'], depth + 1)

    def recursive_search(node):
        if isinstance(node, dict):
            if node.get('id') == target_id:
                collect_descendants(node.get('children', []), depth=1)
                return True
            for key in node:
                if recursive_search(node[key]):
                    return True
        elif isinstance(node, list):
            for item in node:
                if recursive_search(item):
                    return True
        return False  # pragma: no cover

    recursive_search(data)
    return result


def get_cite_button(entity: PresentationView) -> dict[str, str]:
    if not entity:  # pragma: no cover
        return {'button_html': '', 'modal_html': ''}
    current_date = datetime.date.today().strftime("%Y-%m-%d")
    projects = {e.case_study: e for e in g.config_entities if e.case_study}
    case_studies = []
    for type_ in entity.types:
        if cs := projects.get(int(type_.id)):
            case_studies.append(cs)
    if not case_studies:
        case_studies = [e for e in g.config_entities
                        if e.class_id == g.config_classes['main-project']]
    project_name = '/'.join(
        [cs.name['display']['label'] for cs in case_studies])
    button_html = render_template('cite/button.html')
    modal_html = render_template(
        'cite/modal.html',
        entity=entity,
        project_name=project_name,
        projects=case_studies,
        current_url=url_for('entity_view', id_=entity.id, _external=True),
        today_date=current_date)
    return {'button_html': button_html, 'modal_html': modal_html}
