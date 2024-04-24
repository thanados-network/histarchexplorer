from typing import Any


from flask_babel import lazy_gettext as _

from histarchexplorer import app


@app.context_processor
def inject_menu() -> dict[str, Any]:
    navbar = [
        {'original': 'entities', 'title': _('browse/select/find all entities'), 'translation': _('entities')},
        {'original': 'search', 'title': _('detailed search'), 'translation': _('search')},
        {'original': 'about', 'title': _('about the project'), 'translation': _('about')}],
    return {'navbar': navbar}

