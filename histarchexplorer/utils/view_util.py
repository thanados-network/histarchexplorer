import datetime
import re
from pathlib import Path
from typing import Any, Optional
from unicodedata import normalize
from urllib.parse import urlsplit

from flask import g, render_template, render_template_string, url_for
from flask_babel import gettext as _
from flask_login import current_user

from histarchexplorer import app
from histarchexplorer.api.api_access import ApiAccess
from histarchexplorer.api.presentation_view import PresentationView
from histarchexplorer.models.admin import Admin

_('entities')
_('search')
_('about')
_('outcome')
_('publications')


def render_page_template(page_name: str, **context: Any) -> str:
    template_name = f"{page_name}.html"
    if page_name == 'index':
        key = 'start_page'
    else:
        key = page_name.replace('-', '_')

    menu_settings = g.settings.menu_management.get(key, {})

    if menu_settings.get('page_type') == 'individual':
        page_path = Path(app.root_path)/'..'/'uploads'/'templates'/template_name
        if page_path.is_file():
            template_content = page_path.read_text(encoding='utf-8')
            return render_template_string(template_content, **context)

    return render_template(template_name, **context)


@app.template_filter("domain")
def domain_filter(url: str) -> str:
    return urlsplit(url).netloc


@app.context_processor
def inject_menu() -> dict[str, Any]:
    navbar = []
    menu_config = g.settings.menu_management


    navbar.append({'entities': _('browse/select/find all entities')})

    if menu_config.get('search', {}).get('show', True):
        navbar.append({'search': _('detailed search')})

    if menu_config.get('publications', {}).get('show', True):
        navbar.append({'publications': _('Publications')})

    if menu_config.get('outcome', {}).get('show', True):
        navbar.append({'outcome': _('Outcome')})

    if menu_config.get('about', {}).get('show', True):
        navbar.append({'about': _('about the project')})

    return {'navbar': navbar}


def find_children_by_id(
        data: dict[str, Any],
        target_id: Optional[int]) -> list[dict[str, str]] | None:
    result: list[dict[str, str]] = []

    if target_id is None:
        return result

    def collect_descendants(
            children: list[dict[str, Any]],
            depth: int = 1) -> None:
        for child in children:
            prefix = '-' * depth
            name = child.get('name', _('Unknown'))
            result.append({'id': int(child['id']), 'name': f"{prefix}{name}"})
            sub_children = child.get('children')
            if isinstance(sub_children, list) and sub_children:
                collect_descendants(sub_children, depth + 1)

    def recursive_search(node: Any) -> bool:
        if isinstance(node, dict):
            node_id = node.get('id')
            if node_id is not None and int(node_id) == target_id:
                children = node.get('children')
                if isinstance(children, list):
                    collect_descendants(children)
                return True

            for value in node.values():
                if recursive_search(value):
                    return True

        elif isinstance(node, list):
            for item in node:
                if recursive_search(item):
                    return True
        return False

    recursive_search(data)
    return result


def get_license_info(case_studies: list[Any]) -> dict[str, Any] | None:
    all_licenses = {l['id']: l for l in Admin.get_licenses()}

    for project in case_studies:
        if project.license_id and project.license_id in all_licenses:
            return all_licenses[project.license_id]

    main_projects = [
        e for e in g.config_entities
        if e.class_id == g.config_classes['main-project']]
    for mp in main_projects:
        if mp.license_id and mp.license_id in all_licenses:
            return all_licenses[mp.license_id]
    for lic in all_licenses.values():
        if lic['spdx_id'] == 'InC':
            return lic

    return list(all_licenses.values())[0] if all_licenses else None


def generate_bibtex(
        entity: Any,
        project_name: str = None,
        url: str = None,
        date: str = None,
        main_reference: Any = None) -> str:
    if hasattr(entity, 'id'):  # PresentationView
        year = date.split('-')[0] if date else datetime.date.today().year
        title = entity.title
        author = project_name or _('Unknown Project')
        key = f"{slugify(author)}_{entity.id}_{year}"
        url = url or ""
        note = f"{_('Accessed')}: {date}" if date else ""
        if main_reference:
            ref_text = main_reference.citation or main_reference.title
            pages = (main_reference.pages or "").replace("##main", "").strip()
            if pages:
                ref_text = f"{ref_text} {pages}"
            after_text = f"{_('after')} {ref_text}"
            note = f"{after_text}, {note}" if note else after_text
    else:  # Publication dict
        year = entity.get('year') or datetime.date.today().year
        title = entity.get('title')
        author = entity.get('authors') or _('Unknown Author')
        key = f"{slugify(author.split(',')[0])}_{year}"
        url = entity.get('doi') or entity.get('url') or ""
        if entity.get('doi'):
            url = f"https://doi.org/{url}"
        note = ""

    bibtex = f"@misc{{{key},\n"
    bibtex += f"  title = {{{title}}},\n"
    bibtex += f"  author = {{{author}}},\n"
    bibtex += f"  year = {{{year}}},\n"
    bibtex += f"  url = {{{url}}}"
    if note:
        bibtex += f",\n  note = {{{note}}}"
    bibtex += "\n}"
    return bibtex


def generate_ris(
        entity: Any,
        project_name: str = None,
        url: str = None,
        date: str = None,
        main_reference: Any = None) -> str:
    """Generates a RIS citation string."""
    note = ""
    if hasattr(entity, 'id'):  # PresentationView
        year = date.split('-')[0] if date else datetime.date.today().year
        title = entity.title
        author = project_name or _('Unknown Project')
        url = url or ""
        if main_reference:
            ref_text = main_reference.citation or main_reference.title
            pages = (main_reference.pages or "").replace("##main", "").strip()
            if pages:
                ref_text = f"{ref_text} {pages}"
            note = f"{_('after')} {ref_text}"
    else:  # Publication dict
        year = entity.get('year') or datetime.date.today().year
        title = entity.get('title')
        author = entity.get('authors') or _('Unknown Author')
        url = entity.get('doi') or entity.get('url') or ""
        if entity.get('doi'):
            url = f"https://doi.org/{url}"

    ris = "TY  - ELEC\n"
    ris += f"TI  - {title}\n"
    ris += f"AU  - {author}\n"
    ris += f"PY  - {year}\n"
    ris += f"UR  - {url}\n"
    if date:
        ris += f"Y2  - {date}\n"  # Access date
    if note:
        ris += f"N1  - {note}\n"
    ris += "ER  -"
    return ris


def get_publication_citation(pub: dict[str, Any]) -> dict[str, str]:
    authors = pub.get('authors') or _('Unknown Author')
    year = pub.get('year') or ''
    title = pub.get('title') or ''
    doi = pub.get('doi')
    url = pub.get('url')

    # APA style
    apa = f"{authors} ({year}). {title}."
    if doi:
        apa += f" https://doi.org/{doi}"
    elif url:
        apa += f" {url}"

    return {
        'apa': apa,
        'bibtex': generate_bibtex(pub),
        'ris': generate_ris(pub)
    }


def get_cite_button(entity: PresentationView) -> dict[str, str]:
    if not entity:  # pragma: no cover
        return {'button_html': '', 'modal_html': ''}

    current_date = datetime.date.today().strftime("%Y-%m-%d")
    projects = {e.case_study: e for e in g.config_entities if e.case_study}
    case_studies = []
    for type_ in entity.types:
        if cs := projects.get(int(type_.id)):
            case_studies.append(cs)

    # If no specific case study found, use main project(s) as fallback context
    if not case_studies:
        case_studies = [e for e in g.config_entities
                        if e.class_id == g.config_classes['main-project']]

    project_name = '/'.join(
        [cs.name['display']['label'] for cs in case_studies])

    current_url = url_for('entity_view', id_=entity.id, _external=True)

    main_reference = None
    # todo: if a entity has only one bibligraphy, this is the main ref.
    #   what happens if there are multiple bibliography entries?
    for ref in entity.references:
        if ref.pages and '##main' in ref.pages:
            main_reference = ref
            break
        if ref.system_class == 'bibliography':
            main_reference = ref

    license_info = get_license_info(case_studies)
    bibtex = generate_bibtex(
        entity, project_name, current_url, current_date, main_reference)
    ris = generate_ris(
        entity, project_name, current_url, current_date, main_reference)

    # APA-like citation style
    year = current_date.split('-')[0]
    citation_text = (
        f"{project_name} ({year}). {entity.title}. "
        f"{_('Retrieved from')} {current_url} "
        f"({_('Accessed')}: {current_date})")
    if main_reference:
        ref_text = main_reference.citation or main_reference.title
        pages = (main_reference.pages or "").replace("##main", "").strip()
        if pages:
            ref_text = f"{ref_text} {pages}"
        citation_text = f"{citation_text}\n{_('after')} {ref_text}"

    button_html = render_template('util/cite/button.html')
    modal_html = render_template(
        'util/cite/modal.html',
        entity=entity,
        project_name=project_name,
        projects=case_studies,
        current_url=current_url,
        today_date=current_date,
        license=license_info,
        bibtex=bibtex,
        ris=ris,
        citation_text=citation_text
    )
    return {'button_html': button_html, 'modal_html': modal_html}


def get_refresh_button(id_: int) -> str | None:
    if not current_user.is_authenticated:
        return None
    return render_template('util/clear_entity_cache.html', id_=id_)


def get_view_class_count(type_id: Optional[int] = None) -> dict[str, Any]:
    entities_count = ApiAccess.get_entities_count_by_case_studies(type_id)

    for key in entities_count.copy():
        if key not in g.settings.shown_classes:
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


def slugify(value: str) -> str:
    if not value:
        return ""
    value = normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")
