from typing import Any, Optional

from flask import Response, g, redirect, render_template, url_for
from flask.typing import ResponseValue

from histarchexplorer import app
from histarchexplorer.models.config import ConfigEntity
from histarchexplorer.utils.view_util import get_view_class_count, slugify


@app.route('/about', strict_slashes=False)
@app.route('/about/<slug>')
def about(slug: Optional[str] = None) -> Response | str | ResponseValue:
    grouped = ConfigEntity.group_by_class_name(g.config_entities)
    main_project = grouped['main-project'][0]
    sub_projects = grouped.get('project', [])

    config_entities_mapped = {e.id: e for e in g.config_entities}

    projects_by_slug = {}
    for p in [main_project] + sub_projects:
        s = slugify(p.acronym)
        projects_by_slug[s] = p

    if slug:
        active = projects_by_slug.get(slug)
        if not active:
            return redirect(url_for('about'))
    else:
        active = main_project

    project_choices = []
    if slug:
        for p in [main_project] + sub_projects:
            if p is not active:
                project_choices.append(p)
    else:
        project_choices = sub_projects

    people_map = {}
    institutions_map = {}
    institutions_by_role: dict[Any, Any] = {}

    for link in active.links:
        target = next(
            (e for e in g.config_entities if e.id == link.end_id), None)
        if not target:
            continue

        role = None
        if link.role and link.role['display']:
            role = link.role['display'].get('label', '')

        if target.class_name == "person":
            if target.id not in people_map:
                people_map[target.id] = {"entity": target, "roles": []}
            if role:
                people_map[target.id]["roles"].append(role)

        elif target.class_name == "institution":
            if target.id not in institutions_map:
                institutions_map[target.id] = {"entity": target, "roles": []}
            if role:
                institutions_map[target.id]["roles"].append(role)
                institutions_by_role.setdefault(role, []).append(target)
    return render_template(
        "about.html",
        active=active,
        main_project=main_project,
        sub_projects=project_choices or sub_projects,
        config_entities_mapped=config_entities_mapped,
        people=list(people_map.values()),
        institutions_by_role=institutions_by_role,
        slugify=slugify,
        view_class_count=get_view_class_count(active.case_study))
