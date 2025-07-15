from collections import defaultdict
from typing import Any, Optional

from flask import g

from histarchexplorer.database.admin import (
    add_link, add_new_map, check_sortorder, add_entry, delete_entry,
    delete_link,
    delete_map,
    get_config_class_by_id, set_hidden_classes,
    set_index_background,
    set_shown_classes, update_config_entry, update_map)
from histarchexplorer.database.map import get_maps


class EntryNotFound(Exception):
    pass


class Admin:
    class TooManyMainProjects(Exception):
        pass

    @staticmethod
    def set_hidden_classes(form: list[str]) -> None:
        return set_hidden_classes(form)

    @staticmethod
    def set_shown_classes(form: list[str]) -> None:
        return set_shown_classes(form)

    @staticmethod
    def set_index_background(settings: dict[str, str]) -> None:
        return set_index_background(settings)

    @staticmethod
    def add_new_map(data: dict[str, str]) -> int:
        return add_new_map(data)

    @staticmethod
    def delete_map(map_id: int) -> None:
        return delete_map(map_id)

    @staticmethod
    def update_map(data: dict[str, str]) -> None:
        return update_map(data)

    @staticmethod
    def add_entry(data: dict) -> int:
        return add_entry(data)

    @staticmethod
    def edit_entry(data: dict) -> None:
        return update_config_entry(data)

    @staticmethod
    def add_link(data: dict[str, Any]) -> None:
        return add_link(data)

    @staticmethod
    def delete_link(id_: int) -> None:
        return delete_link(id_)

    @staticmethod
    def check_sortorder() -> int:
        return check_sortorder()

    @staticmethod
    def get_config_config_classes_by_id(id_: int) -> int | None:
        return get_config_class_by_id(id_)

    @staticmethod
    def delete_entry(id_: int) -> None:
        return delete_entry(id_)

    @staticmethod
    def get_maps() -> tuple[str]:
        return get_maps()

    @staticmethod
    def _has_translation(entity, field) -> bool:
        value = getattr(entity, field, None)
        return bool(value and value.get(g.language))

    @staticmethod
    def process_entities_by_tab(tabs: list[dict], entry: Optional[str]) -> \
    dict[
        str, list[dict[str, Any]]]:
        result = {}
        for t_data in tabs:
            tab_id = t_data['id']
            tab_target = t_data['target']

            filtered = []
            for entity in filter(lambda e: e.class_id == tab_id,
                                 g.config_entities):
                entity_dict = entity.__dict__.copy()

                for field in ['name', 'description', 'imprint', 'legal_notice',
                              'address']:
                    entity_dict[
                        f"{field}_has_current_translation"] = (
                        Admin._has_translation(
                        entity, field))

                is_active = (tab_target + str(entity.id) == entry)
                entity_dict.update({
                    'is_active_entry': is_active,
                    'is_collapsed_entry': not is_active
                })

                filtered.append(entity_dict)
            result[tab_target] = filtered
        return result

    @staticmethod
    def process_links_by_entity() -> dict[int, list[dict[str, Any]]]:
        result = defaultdict(list)
        for link in g.config_links:
            link_dict = link.__dict__.copy()
            for field in ['config_property', 'end_name', 'role', 'start_name']:
                link_dict[f"{field}_display_label"] = \
                getattr(link, field)['display']['label']
            result[link.start_id].append(link_dict)
        return dict(result)

    @staticmethod
    def process_properties_by_tab(tabs: list[dict]) -> dict[
        str, list[dict[str, Any]]]:
        result = {}
        for t_data in tabs:
            tab_id = t_data['id']
            tab_target = t_data['target']
            props = [
                {**prop.__dict__,
                 'name_display_label': prop.name['display']['label']}
                for prop in g.config_properties if prop.domain == tab_id
            ]
            result[tab_target] = props
        return result

    @staticmethod
    def process_roles() -> list[dict[str, Any]]:
        return [
            {**entity.__dict__,
             'name_display_label': entity.name['display']['label']}
            for entity in g.config_entities
            if entity.class_id == g.config_classes['attribute']
        ]

    @staticmethod
    def process_target_nodes() -> list[dict[str, Any]]:
        return [
            {**entity.__dict__,
             'name_display_label': entity.name['display']['label']}
            for entity in g.config_entities
        ]
