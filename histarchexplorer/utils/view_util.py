from typing import Any

from flask import g
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

def construct_admin_tabs() -> list[dict[str, str | int]]:
    return [
        {
            'label': _('main-project'),
            'target': 'nav-main-project',
            'id': g.config_types['main-project']
        }, {
            'label': _('projects'),
            'target': 'nav-projects',
            'id': g.config_types['project']
        }, {
            'label': _('persons'),
            'target': 'nav-persons',
            'id': g.config_types['person']
        }, {
            'label': _('institutions'),
            'target': 'nav-institutions',
            'id': g.config_types['institution']
        }, {
            'label': _('attributes'),
            'target': 'nav-attributes',
            'id': g.config_types['attribute']}]
