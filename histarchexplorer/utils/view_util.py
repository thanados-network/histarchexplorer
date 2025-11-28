import datetime
from typing import Any, Optional
from urllib.parse import urlsplit

from flask import g, render_template, url_for
from flask_babel import lazy_gettext as _
from flask_login import current_user

from histarchexplorer import app
from histarchexplorer.api.api_access import ApiAccess
from histarchexplorer.api.presentation_view import PresentationView
from histarchexplorer.database.settings import get_shown_classes

_('entities')
_('search')
_('about')


@app.template_filter("domain")
def domain_filter(url):
    return urlsplit(url).netloc


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
    button_html = render_template('util/cite/button.html')
    modal_html = render_template(
        'util/cite/modal.html',
        entity=entity,
        project_name=project_name,
        projects=case_studies,
        current_url=url_for('entity_view', id_=entity.id, _external=True),
        today_date=current_date)
    return {'button_html': button_html, 'modal_html': modal_html}


def get_refresh_button(id_: int) -> str | None:
    """Return HTML for the refresh cache button if user is logged in."""
    if not current_user.is_authenticated:
        return None
    return render_template('util/clear_entity_cache.html', id_=id_)


def get_view_class_count(type_id: Optional[int] = None) -> dict[str, Any]:
    entities_count = ApiAccess.get_entities_count_by_case_studies(type_id)

    for key in entities_count.copy():
        if key not in get_shown_classes():
            del entities_count[key]

    return_classes: dict[str, dict[str, Any]] = {}
    for view_class in g.view_classes:
        for key, value in entities_count.items():
            if key in g.view_classes[view_class]:
                if view_class not in return_classes:
                    return_classes[view_class] = {'count': 0, 'subunits': []}
                return_classes[view_class]['subunits'].append({key: value})
                return_classes[view_class]['count'] += value

    return return_classes
