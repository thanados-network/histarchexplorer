from __future__ import annotations

import re
from typing import Any, Optional

from flask import session, url_for, g

from histarchexplorer import app, cache
from histarchexplorer.api.api_access import ApiAccess
from histarchexplorer.api.parser import Parser
from histarchexplorer.models.depiction import Depiction
from histarchexplorer.models.relation import Relation
from histarchexplorer.models.types import Types
from histarchexplorer.models.util import date_template_format, format_date, \
    split_date_string, uc_first


def get_alias(names) -> str:
    if names:
        return ', '.join(map(str, [a['alias'] for a in names]))
    return ''


def get_types(types) -> list[Types]:
    if types:
        return [Types(types) for types in types]
    return []


def get_relation_class(relations) -> list[Relation]:
    relation = []
    if relations:
        relation = [Relation(relation) for relation in relations]
    return relation


class Entity:
    def __init__(self, json: dict[str, Any]) -> None:
        data = json['features'][0]
        self.id = int(data['@id'].rsplit('/', 1)[-1])
        self.name = data['properties']['title']
        self.description = self.get_description(data['descriptions'])
        self.description_class = self.get_description_class()
        self.system_class = uc_first(
            data['systemClass'].replace('_', ' '))
        self.view_class = uc_first(
            data['viewClass'].replace('_', ' ')) \
            if data.get('viewClass') else None
        self.types = get_types(data.get('types'))
        self.standard_type = self.get_standard_type()
        self.alias = get_alias(data.get('names'))
        self.relations = get_relation_class(data.get('relations'))
        self.depictions = self.get_depiction(data.get('depictions'))
        self.reference_systems = data.get('links')
        self.begin_from = None
        self.begin_to = None
        self.begin_comment = None
        self.end_from = None
        self.end_to = None
        self.begin = None
        self.end = None
        self.parent = self.get_parent()
        self.subunits = self.get_subunits()
        self.geometry = data.get('geometry')
        if 'when' in data:
            self.begin_from = split_date_string(
                data['when']['timespans'][0]['start']['earliest'])
            self.begin_to = split_date_string(
                data['when']['timespans'][0]['start']['latest'])
            self.end_from = split_date_string(
                data['when']['timespans'][0]['end']['earliest'])
            self.end_to = split_date_string(
                data['when']['timespans'][0]['end']['latest'])
            self.begin = format_date(self.begin_from, self.begin_to)
            self.end = format_date(self.end_from, self.end_to)
            self.formated_date = date_template_format(self.begin, self.end)

    def __repr__(self) -> str:  # pragma: no cover
        return str(self.__dict__)

    def get_depiction(self, depictions: Optional[list[dict[str, str]]]) -> list[Depiction]:
        if not depictions:
            return []
        result = []
        for data in depictions:
            id_ = int(data['@id'].rsplit('/', 1)[-1])
            mimetype = data.get("mimetype")
            render_type = (
                "3d_model" if mimetype in {"model/gltf-binary", "model/glb", "model/gltf+json"}
                else "webp" if mimetype in {"image/webp", "image/webp"}
                else "image" if mimetype and mimetype.startswith("image/")
                else "pdf" if mimetype == "application/pdf"
                else "unknown"
            )
            main_image = g.main_images.get(self.id) == id_
            iiif_manifest = ""
            if data.get("IIIFManifest"):
                iiif_manifest = f'{data["IIIFManifest"]}?url={url_for("index", _external=True)}'
            depiction = Depiction(
                id_=id_,
                link=data.get("@id"),
                title=data.get("title"),
                license=data.get("license"),
                license_holder=data.get("licenseHolder"),
                creator=data.get("creator"),
                url=data.get("url"),
                mimetype=mimetype,
                iiif_manifest=iiif_manifest if mimetype.startswith("image/") else None,
                iiif_base_path=data.get("IIIFBasePath"),
                entity_id=self.id,
                main_image=main_image,
                render_type=render_type,
            )
            result.append(depiction)
        return result

    def get_parent(self) -> Optional[Relation]:
        if not self.relations:
            return None
        parent_relation = None
        for relation in self.relations:
            if relation.relation_type in [
                'crm:P46i_forms_part_of',
                'crm:P9i_forms_part_of',
                'crm:P107i_is_current_or_former_member_of']:
                parent_relation = relation
                break
        return parent_relation

    def get_standard_type(self) -> Optional[Types]:
        for type_ in self.types:
            type_.root_id = (
                int(type_.type_hierarchy[0]['identifier'].rsplit('/', 1)[-1]))
            if type_.root in app.config['STANDARD_TYPES']:
                return type_
        return None

    def get_description_class(self) -> str:
        description_class = "item"
        if self.description and len(self.description) > 1500:
            description_class = "item-middle"
        return description_class

    def get_subunits(self) -> list[Relation]:
        if not self.relations:
            return []
        subunit = []
        for relation in self.relations:
            if relation.relation_type in [
                'crm:P46_is_composed_of',
                'crm:P9_consists_of',
                'crm:P107_has_current_or_former_member']:
                subunit.append(relation)
        return subunit

    def to_serializable(self: Any) -> Any:
        if isinstance(self, list):
            return [Entity.to_serializable(item) for item in self]
        elif hasattr(self, "__dict__"):
            return {
                key: Entity.to_serializable(value)
                for key, value in self.__dict__.items()}
        elif isinstance(self, dict):
            return {
                key: Entity.to_serializable(value)
                for key, value in self.items()}
        return self

    @staticmethod
    def get_entity(id_: int, parser: Parser) -> Entity:
        return Entity(ApiAccess.get_entity(id_, parser))

    # @staticmethod
    # def get_entities_linked_to_entity(
    #         id_: int,
    #         parser: Parser) -> list[Entity]:
    #     return [Entity(entity) for entity in
    #             ApiAccess.get_entities_linked_to_entity(id_, parser)]
    #
    # @staticmethod
    # def get_by_system_class(class_: str, parser: Parser) -> list[Entity]:
    #     return [Entity(entity) for entity in
    #             ApiAccess.get_by_system_class(class_, parser)]

    @staticmethod
    @cache.memoize()
    def get_linked_entities_by_properties_recursive(
            id_: int,
            parser: Parser) -> list[Entity]:
        return [Entity(entity) for entity in
                ApiAccess.linked_entities_by_properties_recursive(id_, parser)]

    @staticmethod
    def get_description(data: list[dict[str, Any]]) -> str:
        if not data or not data[0]['value']:
            return ''
        description = [i['value'] for i in data][0]

        # ##en_##English text##_en## -> [('en', 'English text')]
        matches = re.findall(r'##(\w+)_##(.*?)##_\1##', description, re.DOTALL)
        if matches:
            lang_dict = {lang: text.strip() for lang, text in matches}
            return lang_dict.get(session['language'], description)

        description = description.split('##German')
        if len(description) > 1:
            lang_dict = {
                'en': description[0],
                'de': description[1]}
            description = lang_dict.get(
                session['language'],
                description[0])  # fallback

        if isinstance(description, list):
            description = description[0]
        return description
