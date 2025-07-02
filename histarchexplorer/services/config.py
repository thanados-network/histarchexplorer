from collections import defaultdict
from dataclasses import dataclass
from typing import Any

from flask import g
from flask_babel import lazy_gettext as _

from histarchexplorer.database.about import (
    get_affiliations, get_config_entities, get_project_attributes_sql)
from histarchexplorer.database.admin import get_config_links, \
    get_config_properties
from histarchexplorer.database.config_classes import get_config_classes_sql


def get_config_classes() -> dict[str, int]:
    data = {}
    for config_class in get_config_classes_sql():
        data[config_class.name] = config_class.id
    return data


@dataclass()
class Link:
    link_id: int
    sortorder: int
    start_id: int
    start_name: dict[str, str | dict[str, str]]
    config_property: dict[str, str | dict[str, str]]
    property_id: int
    direction: str
    end_name: dict[str, str | dict[str, str]]
    end_id: int
    role: dict[str, str | dict[str, str]]
    role_id: int

    @classmethod
    def get_all(cls) -> list['Link']:
        links = []
        for link_ in get_config_links():
            links.append(Link(
                link_id=link_.link_id,
                sortorder=link_.sortorder,
                start_id=link_.start_id,
                start_name=add_display(link_.start_name),
                config_property=add_display(link_.config_property),
                property_id=link_.property_id,
                direction=link_.direction,
                end_name=add_display(link_.end_name),
                end_id=link_.end_id,
                role=add_display(link_.role),
                role_id=link_.role_id))
        return links


@dataclass()
class Properties:
    id: int
    name: dict[str, str | dict[str, str]]
    domain: int
    range: int
    direction: str

    @classmethod
    def get_all(cls) -> list['Properties']:
        properties = []
        for property_ in get_config_properties():
            properties.append(Properties(
                id=property_.id,
                name=add_display(property_.name),
                domain=property_.domain_type_id,
                range=property_.range_type_id,
                direction=property_.direction))
        return properties


@dataclass()
class ConfigEntity:
    id: int
    name: dict[str, str | dict[str, str]]
    description: dict[str, str | dict[str, str]]
    website: str
    legal_notice: dict[str, str | dict[str, str]]
    imprint: dict[str, str | dict[str, str]]
    class_id: int
    address: dict[str, str | dict[str, str]]
    email: str
    image: str
    orcid_id: str
    class_name: str
    attributes: dict[int, list[str]] | None
    main_project: bool
    affiliations: list[dict[str, Any]] | None

    @classmethod
    def get_all_localized(cls) -> list['ConfigEntity']:
        entities = []

        for entry in get_config_entities():
            entities.append(ConfigEntity(
                id=entry.id,
                name=add_display(entry.name),
                description=add_display(entry.description),
                website=entry.website,
                legal_notice=add_display(entry.legal_notice),
                imprint=add_display(entry.imprint),
                class_id=entry.class_id,
                address=add_display(entry.address),
                email=entry.email,
                image=entry.image,
                orcid_id=entry.orcid_id,
                class_name=entry.class_name,
                main_project=(entry.class_name == 'main-project'),
                attributes=get_project_roles(
                    entry.id,
                    entry.class_id),
                affiliations=get_person_affiliations(entry.id)
                if entry.class_name == 'person' else None
            ))

        return entities

    @classmethod
    def group_by_class_name(
            cls,
            entities: list['ConfigEntity']) \
            -> dict[str, list['ConfigEntity']]:
        grouped = {}
        for entity in entities:
            grouped.setdefault(entity.class_name, []).append(entity)
        return grouped


def get_project_roles(
        id_: int,
        config_class_id: int) -> dict[int, list]:
    result = defaultdict(list)
    for domain_id, attribute in get_project_attributes_sql(
            id_,
            config_class_id):
        if attribute:
            result[domain_id].append(localize(attribute))
        else:
            result[domain_id].append(_('no attribute'))
    return dict(result)


def get_person_affiliations(id_: int) -> list[dict[str, Any]]:
    grouped = defaultdict(lambda: {"attributes": []})
    for record in get_affiliations(id_):
        rid = record.range_id
        if "id" not in grouped[rid]:
            grouped[rid]["institute_id"] = rid
            grouped[rid]["affiliation"] = localize(record.affiliation)
        grouped[rid]["attributes"].append(localize(record.attribute))
    return list(grouped.values())


def localize(data: dict[str, str] | None) -> str | None:
    selected_lang = g.language
    if not isinstance(data, dict):
        return data

    # Try selected language
    if selected_lang in data and data[selected_lang]:
        return data[selected_lang]

    # Fallback to g.preferred_langauge
    if g.preferred_langauge in data and data[g.preferred_langauge]:
        return data[g.preferred_langauge]

    # Fallback to any filled value
    for value in data.values():
        if value:
            return value

    return None


def add_display(data: dict[str, Any]) -> dict[str, Any] | None:
    if not data:
        return {}
    result = data.copy()
    label = localize(data)

    for lang, value in data.items():
        if value == label:
            result['display'] = {'language': lang, 'label': label}
            break
    else:
        result['display'] = {'language': None, 'label': label}

    return result
