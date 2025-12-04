from collections import defaultdict
from typing import Any, Optional

from flask import g

from histarchexplorer.database.admin import (
    add_entry, add_link, add_new_map,
    check_sortorder, delete_entry,
    delete_link, delete_map,
    get_config_class_by_id,
    get_openatlas_entity,
    set_hidden_classes,
    set_index_background,
    set_shown_classes,
    update_case_study_type_hierarchy, update_config_entry, update_map)
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
    def _has_translation(entity, field_key) -> bool:
        value_attr = getattr(entity, field_key, None)

        if isinstance(value_attr, dict) and 'display' in value_attr:
            return bool(value_attr['display'].get(g.language))
        elif value_attr is not None:
            return True
        return False

    @staticmethod
    def process_entities_by_tab(
            tabs: list[dict],
            entry: Optional[str]) -> dict[str, list[dict[str, Any]]]:
        result = {}
        for t_data in tabs:
            tab_id = t_data['id']
            tab_target = t_data['target']
            fields_for_tab = g.admin_fields.get(tab_target, [])
            filtered = []
            for entity in filter(
                    lambda e: e.class_id == tab_id, g.config_entities):
                entity_dict = {'id': entity.id, 'class_id': entity.class_id}
                for field_config in fields_for_tab:
                    field_key = field_config['key']
                    is_translatable = field_config.get('translatable', False)
                    if is_translatable:
                        entity_dict[f"{field_key}_has_current_translation"] = \
                            Admin._has_translation(entity, field_key)
                    else:
                        entity_dict[
                            f"{field_key}_has_current_translation"] = bool(
                            getattr(entity, field_key, None))

                    raw_field_value = getattr(entity, field_key, None)

                    if (is_translatable and isinstance(raw_field_value, dict)
                            and 'display' in raw_field_value):
                        entity_dict[f"{field_key}_display_label"] = (
                            raw_field_value['display'].get('label', ''))
                        entity_dict[field_key] = raw_field_value
                    elif raw_field_value is not None:
                        entity_dict[f"{field_key}_display_label"] = \
                            raw_field_value
                        entity_dict[field_key] = raw_field_value
                    else:
                        entity_dict[f"{field_key}_display_label"] = ''
                        entity_dict[field_key] = None

                is_active = (tab_target + str(entity.id) == entry)
                entity_dict.update({
                    'is_active_entry': is_active,
                    'is_collapsed_entry': not is_active,
                    'fields_config': fields_for_tab})

                filtered.append(entity_dict)
            result[tab_target] = filtered
        return dict(result)

    @staticmethod
    def process_links_by_entity() -> dict[int, list[dict[str, Any]]]:
        result = defaultdict(list)
        for link in g.config_links:
            link_dict = link.__dict__.copy()
            for field in ['config_property', 'end_name', 'role', 'start_name']:
                field_obj = getattr(link, field, None)
                if isinstance(field_obj, dict) and 'display' in field_obj:
                    link_dict[f"{field}_display_label"] = field_obj['display'][
                        'label']
                else:
                    link_dict[f"{field}_display_label"] = str(field_obj)
            result[link.start_id].append(link_dict)
        return dict(result)

    @staticmethod
    def process_properties_by_tab(
            tabs: list[dict]) -> dict[str, list[dict[str, Any]]]:
        result = {}
        for t_data in tabs:
            tab_id = t_data['id']
            tab_target = t_data['target']
            props = []
            for prop in g.config_properties:
                if prop.domain == tab_id:
                    prop_dict = prop.__dict__.copy()
                    if isinstance(prop.name, dict) and 'display' in prop.name:
                        prop_dict['name_display_label'] = prop.name['display'][
                            'label']
                    else:
                        prop_dict['name_display_label'] = str(prop.name)
                    props.append(prop_dict)
            result[tab_target] = props
        return result

    @staticmethod
    def process_roles() -> list[dict[str, Any]]:
        return [
            {**entity.__dict__,
             'name_display_label': entity.name['display']['label']}
            for entity in g.config_entities
            if entity.class_id == g.config_classes['attribute']]

    @staticmethod
    def process_target_nodes() -> list[dict[str, Any]]:
        return [
            {**entity.__dict__,
             'name_display_label': entity.name['display']['label']}
            for entity in g.config_entities]

    @staticmethod
    def check_case_study_type_id(entity_id: int) -> dict[str, Any]:
        details = Admin.get_openatlas_entity(entity_id)
        if details:
            is_valid = details.openatlas_class_name == 'type'
            return {
                'is_valid': is_valid,
                'name': details.name,
                'class_name': details.openatlas_class_name}
        return {
            'is_valid': False,
            'name': None,
            'class_name': None}

    # Todo: replace with API call
    @staticmethod
    def get_openatlas_entity(entity_id: int) -> Any:
        return get_openatlas_entity(entity_id)

    @staticmethod
    def update_case_study_id_setting(id_: int) -> None:
        return update_case_study_type_hierarchy(int(id_))
