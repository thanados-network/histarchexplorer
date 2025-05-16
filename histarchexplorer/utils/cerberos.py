from typing import Any

from histarchexplorer import app
from histarchexplorer.api.helpers import get_entities_count_by_case_study
from histarchexplorer.database.settings import get_shown_entities


def get_view_class_count() -> dict[str, Any]:
    entities_count  = get_entities_count_by_case_study()

    for key in entities_count.copy():
        if key not in get_shown_entities():
            del entities_count[key]

    return_classes: dict[str, dict[str, Any]] = {}
    view_classes = app.config['VIEW_CLASSES']
    for view_class in view_classes:
        for key, value in entities_count.items():
            if key in view_classes[view_class]:
                if view_class not in return_classes:
                    return_classes[view_class] ={'count':0, 'subunits': []}
                return_classes[view_class]['subunits'].append({key: value})
                return_classes[view_class]['count'] += value

    return return_classes
