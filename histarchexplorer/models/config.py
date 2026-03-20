import html
from dataclasses import dataclass
from typing import Any

from flask import g

from histarchexplorer.database.about import get_config_entities
from histarchexplorer.database.admin import (
    get_config_links,  get_config_properties)
from histarchexplorer.database.config_classes import get_config_classes_sql


def get_config_classes() -> dict[str, int]:
    data = {}
    for config_class in get_config_classes_sql():
        data[config_class['name']] = config_class['id']
    return data


@dataclass()
class Link:
    link_id: int
    sortorder: int
    start_id: int
    start_name: dict[str, dict[str, str | None]]
    config_property: dict[str, dict[str, str | None]]
    property_id: int
    direction: str
    end_name: dict[str, dict[str, str | None]]
    end_id: int
    role: dict[str, dict[str, str | None]]
    role_id: int

    @classmethod
    def get_all(cls) -> list['Link']:
        return [
            Link(
                link_id=link_['link_id'],
                sortorder=link_['sortorder'],
                start_id=link_['start_id'],
                start_name=add_display(link_['start_name']),
                config_property=add_display(link_['config_property']),
                property_id=link_['property_id'],
                direction=link_['direction'],
                end_name=add_display(link_['end_name']),
                end_id=link_['end_id'],
                role=add_display(link_['role']),
                role_id=link_['role_id']
            ) for link_ in get_config_links()
        ]


@dataclass()
class Properties:
    id: int
    name: dict[str, dict[str, str | None]]
    domain: int
    range: int
    direction: str

    @classmethod
    def get_all(cls) -> list['Properties']:
        return [
            Properties(
                id=prop['id'],
                name=add_display(prop['name']),
                domain=prop['domain_type_id'],
                range=prop['range_type_id'],
                direction=prop['direction']
            ) for prop in get_config_properties()
        ]


# pylint: disable=too-many-instance-attributes
@dataclass()
class ConfigEntity:
    id: int
    name: dict[str, dict[str, str | None]]
    acronym: str
    description: dict[str, dict[str, str | None]]
    website: str
    class_id: int
    address: dict[str, dict[str, str | None]]
    email: str
    image: str
    orcid_id: str
    class_name: str
    case_study: int
    main_project: bool
    links: list[Link]
    license_id: int

    @classmethod
    def get_all_localized(cls) -> list['ConfigEntity']:
        return [
            ConfigEntity(
                id=entry['id'],
                name=add_display(entry['name']),
                acronym=entry['acronym'],
                description=add_display(entry['description']),
                website=entry['website'],
                class_id=entry['class_id'],
                address=add_display(entry['address']),
                email=entry['email'],
                image=entry['image'],
                orcid_id=entry['orcid_id'],
                class_name=entry['class_name'],
                case_study=entry['case_study_type_id'],
                main_project=(entry['class_name'] == 'main-project'),
                links=[l for l in g.config_links if l.start_id == entry['id']]
                if g.config_links else [],
                license_id=entry['license_id']
            ) for entry in get_config_entities()
        ]

    @classmethod
    def group_by_class_name(
            cls,
            entities: list['ConfigEntity']) -> dict[str, list['ConfigEntity']]:
        grouped: dict[str, list[ConfigEntity]] = {}
        for entity in entities:
            grouped.setdefault(entity.class_name, []).append(entity)
        return grouped


# def get_project_roles(
#         id_: int,
#         config_class_id: int) -> dict[int, list]:
#     result = defaultdict(list)
#     attributes= get_project_attributes_sql(id_, config_class_id)
#     for domain_id, attribute in attributes:
#         if attribute:
#             result[domain_id].append(localize(attribute))
#     for range_id, attribute in get_project_attributes_sql_inverse(id_,
#     config_class_id):
#         if attribute:
#             result[range_id].append(localize(attribute))
#     return dict(result)


# def get_person_affiliations(id_: int) -> list[dict[str, Any]]:
#     grouped = defaultdict(lambda: {"attributes": []})
#     for record in get_affiliations(id_):
#         rid = record.range_id
#         if "id" not in grouped[rid]:
#             grouped[rid]["id"] = rid
#             grouped[rid]["affiliation"] = localize(record.affiliation)
#         grouped[rid]["attributes"].append(localize(record.attribute))
#     return list(grouped.values())


def localize(data: dict[str, str] | None) -> str | None:
    if not isinstance(data, dict):
        return data

    # Try selected language, then preferred, then any filled value
    for lang in (g.language, g.preferred_langauge):
        if data.get(lang):
            return data[lang]

    return next((v for v in data.values() if v), None)


def add_display(data: dict[str, Any] | None) \
        -> dict[str, dict[str, str | None]]:
    if not data:
        return {'display': {'language': None, 'label': ''}}

    result = data.copy()
    label = localize(data)
    if isinstance(label, str):
        label = html.unescape(label)

    result['display'] = {'language': None, 'label': label}
    for lang, value in data.items():
        if value == label:
            result['display']['language'] = lang
            break

    return result
