from __future__ import annotations

from typing import Any, Optional

from flask import session

from histarchexplorer import app
from histarchexplorer.api.api_access import ApiAccess
from histarchexplorer.api.parser import Parser
from histarchexplorer.models.depiction import Depiction
from histarchexplorer.models.relation import Relation
from histarchexplorer.models.types import Types
from histarchexplorer.models.util import format_date, split_date_string, \
    uc_first, date_template_format


class Entity:
    def __init__(self, json: dict[str, Any]) -> None:
        self.data = json['features'][0]
        self.id = int(self.data['@id'].rsplit('/', 1)[-1])
        self.name = self.data['properties']['title']
        self.description = self.get_description(self.data['descriptions'])
        self.description_class = self.get_description_class()
        self.system_class = uc_first(
            self.data['systemClass'].replace('_', ' '))
        self.view_class = uc_first(
            self.data['viewClass'].replace('_', ' ')) \
            if self.data.get('viewClass') else None
        self.types = self.get_types()
        self.standard_type = self.get_standard_type()
        self.alias = self.get_alias()
        self.relations = self.get_relation_class()
        self.depictions = self.get_depiction()
        self.reference_systems = self.data.get('links')
        self.begin_from = None
        self.begin_to = None
        self.begin_comment = None
        self.end_from = None
        self.end_to = None
        self.begin = None
        self.end = None
        self.parent = self.get_parent()
        self.subunits = self.get_subunits()
        self.geometry = self.handling_geometry(self.data)
        if 'when' in self.data:
            self.begin_from = split_date_string(
                self.data['when']['timespans'][0]['start']['earliest'])
            self.begin_to = split_date_string(
                self.data['when']['timespans'][0]['start']['latest'])
            self.end_from = split_date_string(
                self.data['when']['timespans'][0]['end']['earliest'])
            self.end_to = split_date_string(
                self.data['when']['timespans'][0]['end']['latest'])
            self.begin = format_date(self.begin_from, self.begin_to)
            self.end = format_date(self.end_from, self.end_to)
            self.formated_date = date_template_format(self.begin, self.end)

    def __repr__(self) -> str:
        return str(self.__dict__)

    def get_relation_class(self) -> list[Relation]:
        relation = []
        if relations := self.data.get('relations'):
            relation = [Relation(relation) for relation in relations]
        return relation

    def get_alias(self) -> str:
        if names := self.data.get('names'):
            return ', '.join(map(str, [a['alias'] for a in names]))
        return ''

    def get_types(self) -> list[Types]:
        if self.data.get('types'):
            return [Types(types) for types in self.data['types']]
        return []

    def get_depiction(self) -> list[Depiction]:
        if depictions := self.data.get('depictions'):
            return [Depiction(depiction, self.id) for depiction in depictions]
        return []

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
            if parent_relation:
                break
        return parent_relation

    def get_standard_type(self) -> Optional[Types]:
        for type_ in self.types:
            type_.root_id = (int(type_.type_hierarchy[0]['identifier'].rsplit('/', 1)[-1]))
            if type_.root in app.config['STANDARD_TYPES']:
                # print(type_)
                return type_
        return None

    def get_description_class(self) -> str:
        description_class = "item"
        if self.description and len(self.description) > 500:
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

    @staticmethod
    def get_entity(id_: int, parser: Parser) -> Entity:
        return Entity(ApiAccess.get_entity(id_, parser))

    @staticmethod
    def get_entities_linked_to_entity(
            id_: int,
            parser: Parser) -> list[Entity]:
        return [Entity(entity) for entity in
                ApiAccess.get_entities_linked_to_entity(id_, parser)]

    @staticmethod
    def get_by_system_class(class_: str, parser: Parser) -> list[Entity]:
        return [Entity(entity) for entity in
                ApiAccess.get_by_system_class(class_, parser)]

    @staticmethod
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
        description = description.split('##German')
        if len(description) > 1:
            lang_dict = {
                'en': description[0],
                'de': description[1]}
            description = lang_dict[session['language']]
        return description

    @staticmethod
    def handling_geometry(
            data: dict[str, Any]) -> Optional[list[dict[str, Any]]]:
        if geometry := data.get('geometry'):
            if geometry['type'] == 'GeometryCollection':
                return geometry['geometries']
            return geometry
        return None
