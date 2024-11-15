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
