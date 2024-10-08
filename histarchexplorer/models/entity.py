from __future__ import annotations

from typing import Any, Optional

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
        self.system_class = uc_first(
            self.data['systemClass'].replace('_', ' '))
        self.view_class = uc_first(
            self.data['viewClass'].replace('_', ' ')) \
            if self.data.get('viewClass') else None
        self.types = self.get_types()
        self.alias = self.get_alias()
        self.relation_class = self.get_relation_class()
        self.relations = self.get_relations() if self.relation_class else None
        self.depictions = self.get_depiction()
        self.reference_systems = self.data.get('links')
        self.begin_from = None
        self.begin_to = None
        self.begin_comment = None
        self.end_from = None
        self.end_to = None
        self.begin = None
        self.end = None
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

    def get_relations(self) -> dict[str, list[Relation]]:
        relation_dict: dict[str, Any] = {}
        for relation in self.relation_class:
            match relation.relation_system_class:
                case 'file' | 'appellation' | \
                     'object_location' | 'reference_system':
                    continue
                case 'type':
                    relation_dict.setdefault('types', []).append(relation)
                case 'source':
                    relation_dict.setdefault('sources', []).append(relation)
                case 'source_translation':
                    (relation_dict.setdefault('source_translations', [])
                     .append(relation))

                case 'place' | 'feature' | 'stratigraphic_unit':
                    relation_dict.setdefault('places', []).append(relation)
                case 'administrative_unit':
                    relation_dict.setdefault(
                        'administrative_unit', []).append(relation)
                case 'artifact' | 'human_remains':
                    relation_dict.setdefault('artifacts', []).append(relation)

                case 'bibliography':
                    relation_dict.setdefault('bibliography', []).append(
                        relation)
                case 'external_reference':
                    relation_dict.setdefault('external_references', []).append(
                        relation)
                case 'edition':
                    relation_dict.setdefault('editions', []).append(relation)

                case 'acquisition' | 'activity' | \
                     'event' | 'move' | 'production':
                    relation_dict.setdefault('events', []).append(relation)
                case 'group' | 'person':
                    relation_dict.setdefault('actors', []).append(relation)
                case _:
                    relation_dict.setdefault('others', []).append(relation)
        return relation_dict

    def get_relation_class(self) -> list[Relation]:
        relation = []
        if relations := self.data.get('relations'):
            relation = [Relation(relation) for relation in relations]
        return relation

    def get_alias(self) -> str:
        if names := self.data.get('names'):
            return ', '.join(map(str, [a['alias'] for a in names]))
        return ''

    def get_types(self) -> Optional[list[Types]]:
        if self.data.get('types'):
            return [Types(types) for types in self.data['types']]
        return None

    def get_depiction(self) -> Optional[list[Depiction]]:
        if depictions := self.data.get('depictions'):
            return [Depiction(depiction, self.id) for depiction in depictions]
        return []

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
    def get_description(data: list[dict[str, Any]]) -> Optional[list[str]]:
        return [i['value'] for i in data][0] if data else None

    @staticmethod
    def handling_geometry(
            data: dict[str, Any]) -> Optional[list[dict[str, Any]]]:
        if geometry := data.get('geometry'):
            if geometry['type'] == 'GeometryCollection':
                return geometry['geometries']
            return geometry
        return None
