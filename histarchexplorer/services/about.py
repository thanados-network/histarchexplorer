from collections import defaultdict
from dataclasses import dataclass
from typing import Any

from flask import g
from flask_babel import lazy_gettext as _

from histarchexplorer.database.about import get_affiliations, get_institutions, \
    get_persons, \
    get_project_roles_sql, get_projects


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
                roles=get_project_roles(
                    entry.id,
                    g.config_classes['institution'])))
        return institutions


def get_project_roles(
        id_: int,
        config_class_id: int) -> dict[int, list]:
    result = defaultdict(list)
    for domain_id, role in get_project_roles_sql(id_, config_class_id):
        if role:
            result[domain_id].append(localize(role))
        else:
            result[domain_id].append(_('no role'))
    return dict(result)

def get_person_affiliations(id_: int) -> list[dict[str, Any]]:
    grouped = defaultdict(lambda: {"roles": []})
    for record in get_affiliations(id_):
        rid = record.range_id
        if "id" not in grouped[rid]:
            grouped[rid]["institute_id"] = rid
            grouped[rid]["affiliation"] = localize(record.affiliation)
        grouped[rid]["roles"].append(localize(record.role))
    return list(grouped.values())


@dataclass
class Person:
    id_: int
    name: str
    description: str | None
    email: str | None
    image: str | None
    orcid_id: str | None
    roles: dict[int, list[str]] | None
    affiliations: list[dict[str, Any]] | None

    @classmethod
    def get_all_localized(cls) -> list['Person']:
        results = get_persons()
        persons = []
        for entry in results:
            persons.append(Person(
                id_=entry.id,
                name=localize(entry.name),
                description=localize(entry.description),
                email=entry.email,
                image=entry.image,
                orcid_id=entry.orcid_id,
                roles=get_project_roles(entry.id, g.config_classes['person']),
                affiliations=get_person_affiliations(entry.id)))
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
