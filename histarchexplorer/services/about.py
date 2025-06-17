from collections import defaultdict
from dataclasses import dataclass

from flask import g
from flask_babel import lazy_gettext as _

from histarchexplorer.database.about import get_institutions, get_persons, \
    get_projects


@dataclass
class Project:
    id_: int
    name: str
    description: str | None
    website: str | None
    legal_notice: str | None
    imprint: str | None
    main_project: bool

    @classmethod
    def get_all_localized(cls) -> list['Project']:
        results = get_projects()
        projects = []

        for entry in results:
            projects.append(Project(
                id_=entry.id,
                name=localize(entry.name),
                description=localize(entry.description),
                website=entry.website,
                legal_notice=localize(entry.legal_notice),
                imprint=localize(entry.imprint),
                main_project=(entry.class_name == 'main-project')))

        return projects


@dataclass
class Institution:
    id_: int
    name: str
    description: str | None
    address: str | None
    email: str | None
    website: str | None
    image: str | None
    roles: dict[int, list[str]] | None
    role: str | None  # translated label for view

    @classmethod
    def get_all_localized(cls) -> list['Institution']:
        results = get_institutions()
        institutions = []
        for entry in results:
            institutions.append(Institution(
                id_=entry.id,
                name=localize(entry.name),
                description=localize(entry.description),
                address=localize(entry.address),
                email=entry.email,
                website=entry.website,
                image=entry.image,
                roles=get_project_roles_for_institutions(entry.id),
                role=None))
        return institutions

def get_project_roles_for_institutions(id_: int) -> dict[int, list]:
    g.cursor.execute(f"""
        SELECT 
            l.domain_id,
            role.name AS role
        FROM tng.links l
        JOIN tng.config c ON l.range_id = c.id
        LEFT JOIN tng.config role 
            ON l.attribute = role.id 
            AND role.config_class = {g.config_classes['role']}
        WHERE 
            l.range_id = %s
        AND c.config_class = {g.config_classes['institution']}
        ORDER BY l.sortorder, l.id;
    """, (id_,))

    result = defaultdict(list)
    for domain_id, role in g.cursor.fetchall():
        if role:
            result[domain_id].append(localize(role))
        else:
            result[domain_id].append(_('no role'))

    return dict(result)


def get_project_roles_for_persons(id_):
    pass


# Todo: I'm at the start of person. Get list of attributes right.
#  then make the rest. One thing is, that the view of team has some little errors.
#  so these are not the correct guide line, if something works.
@dataclass
class Person:
    id_: int
    name: str
    description: str | None
    address: str | None
    email: str | None
    website: str | None
    image: str | None
    roles: dict[int, list[str]] | None
    role: str | None  # translated label for view

    @classmethod
    def get_all_localized(cls) -> list['Person']:
        results = get_persons()
        persons = []
        for entry in results:
            persons.append(Institution(
                id_=entry.id,
                name=localize(entry.name),
                description=localize(entry.description),
                address=localize(entry.address),
                email=entry.email,
                website=entry.website,
                image=entry.image,
                roles=get_project_roles_for_persons(entry.id),
                role=None))
        return persons

def localize(data: dict[str, str] | None) -> str | None:
    preferred_lang = g.language
    if not isinstance(data, dict):
        return data

    # Try preferred language
    if preferred_lang in data and data[preferred_lang]:
        return data[preferred_lang]

    # Fallback to English
    if 'en' in data and data['en']:
        return data['en']

    # Fallback to any filled value
    for value in data.values():
        if value:
            return value

    return None
