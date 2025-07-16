from typing import Any

from flask_babel import lazy_gettext as _

from histarchexplorer import app

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
        return False

    recursive_search(data)
    return result


