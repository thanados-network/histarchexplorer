import datetime
from typing import Any, Optional

from flask import Response, g, redirect, request, url_for
from flask.typing import ResponseValue
from flask_babel import gettext as _

from histarchexplorer import app
from histarchexplorer.database.map import get_map_tilestring
from histarchexplorer.models.config import ConfigEntity
from histarchexplorer.services.statistics import (
    build_dynamic_landing_sections, get_landing_statistics)
from histarchexplorer.utils.view_util import (
    get_license_info, get_view_class_count, render_page_template, slugify)


def _extract_initials(full_name: str) -> str:
    """Return up to two uppercase initials from a person's name."""
    parts = [p for p in (full_name or '').strip().split() if p]
    if not parts:
        return '?'
    if len(parts) == 1:
        return parts[0][:2].upper()
    return f'{parts[0][0]}{parts[-1][0]}'.upper()


def _extract_person_affiliations(
        person: ConfigEntity,
        entities_by_id: dict[int, ConfigEntity]) -> list[dict[str, Any]]:
    """Collect unique institutions affiliated with a person."""
    affiliations: list[dict[str, Any]] = []
    seen_ids: set[int] = set()
    for link in person.links:
        target = entities_by_id.get(link.end_id)
        if not target or target.class_name != 'institution':
            continue
        if target.id in seen_ids:
            continue
        seen_ids.add(target.id)
        label = target.name.get('display', {}).get('label') or ''
        affiliations.append({
            'id': target.id,
            'name': label,
            'acronym': target.acronym or label})
    return affiliations


@app.route('/about', strict_slashes=False)
@app.route('/about/<slug>')
def about(slug: Optional[str] = None) -> Response | str | ResponseValue:
    """Render the 'About' page for a project or sub-project.

    Fetches details of the active project (selected via slug, or
    the main project by default), lists team members and institutions
    categorized by their roles, and compiles project statistics, map
    settings, and citation metadata for display.
    """
    grouped = ConfigEntity.group_by_class_name(g.config_entities)
    main_project = grouped['main-project'][0]
    sub_projects = grouped.get('project', [])
    all_projects = [main_project] + sub_projects

    config_entities_mapped = {e.id: e for e in g.config_entities}

    projects_by_slug = {}
    project_slugs = {}
    for p in all_projects:
        s = slugify(p.acronym)
        projects_by_slug[s] = p
        project_slugs[p.id] = '' if p.main_project else s

    if slug:
        active = projects_by_slug.get(slug)
        if not active:
            return redirect(url_for('about'))
    else:
        active = main_project

    project_choices = []
    if slug:
        for p in all_projects:
            if p is not active:
                project_choices.append(p)
    else:
        project_choices = sub_projects

    people_map: dict[int, dict[str, Any]] = {}
    institutions_map: dict[int, dict[str, Any]] = {}
    institutions_by_role: dict[Any, Any] = {}
    team_roles: list[str] = []

    for link in active.links:
        target = config_entities_mapped.get(link.end_id)
        if not target:
            continue

        role = None
        if link.role and link.role.get('display'):
            role = link.role['display'].get('label', '')

        if target.class_name == 'person':
            if target.id not in people_map:
                person_name = (
                    target.name.get('display', {}).get('label') or '')
                people_map[target.id] = {
                    'entity': target,
                    'roles': [],
                    'initials': _extract_initials(person_name),
                    'affiliations': _extract_person_affiliations(
                        target, config_entities_mapped)}
            if role and role not in people_map[target.id]['roles']:
                people_map[target.id]['roles'].append(role)
                if role not in team_roles:
                    team_roles.append(role)

        elif target.class_name == 'institution':
            if target.id not in institutions_map:
                institutions_map[target.id] = {
                    'entity': target,
                    'roles': []}
            effective_role = role or _('Partner')
            if effective_role not in institutions_map[target.id]['roles']:
                institutions_map[target.id]['roles'].append(effective_role)
            role_list = institutions_by_role.setdefault(effective_role, [])
            if target not in role_list:
                role_list.append(target)

    if active.case_study and active.case_study > 0:
        active_cs_tuple = (active.case_study,)
    else:
        active_cs_tuple = tuple(getattr(g, 'case_study_ids', ()) or ())

    view_class_count = get_view_class_count(active.case_study)
    landing_stats = get_landing_statistics(active_cs_tuple)
    kpi_cards, thematic_cards = build_dynamic_landing_sections(
        landing_stats, view_class_count)

    map_data = g.settings.get_map_settings()
    map_ = None
    if index_map := map_data.get('map'):
        map_ = get_map_tilestring(index_map)

    license_info = get_license_info([active])

    current_year = datetime.datetime.now().year
    active_name = (
        active.name.get('display', {}).get('label')
        or active.acronym
        or 'Histarchexplorer')
    active_url = request.base_url
    citation_apa = (
        f'{active_name} ({current_year}). '
        f'Research Data Repository. {active_url}')
    cite_key = f"{slugify(active.acronym or active_name)}_{current_year}"
    citation_bibtex = (
        f'@misc{{{cite_key},\n'
        f'  title = {{{active_name}}},\n'
        f'  year = {{{current_year}}},\n'
        f'  url = {{{active_url}}}\n'
        f'}}')

    return render_page_template(
        'about',
        active=active,
        main_project=main_project,
        all_projects=all_projects,
        project_slugs=project_slugs,
        sub_projects=project_choices or sub_projects,
        config_entities_mapped=config_entities_mapped,
        people=list(people_map.values()),
        team_roles=team_roles,
        institutions=list(institutions_map.values()),
        institutions_by_role=institutions_by_role,
        slugify=slugify,
        view_class_count=view_class_count,
        kpi_cards=kpi_cards,
        thematic_cards=thematic_cards,
        landing_stats=landing_stats,
        map=map_,
        map_data=map_data,
        license_info=license_info,
        citation_apa=citation_apa,
        citation_bibtex=citation_bibtex)
