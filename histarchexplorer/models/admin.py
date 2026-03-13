from collections import defaultdict
from typing import Any, Optional

from flask import g

from histarchexplorer.database.admin import (
    add_entry, add_license, add_link,
    add_new_map, check_sortorder,
    delete_entry, delete_license,
    delete_link, delete_map,
    get_config_class_by_id,
    get_file_licenses, get_licenses,
    get_openatlas_entity,
    update_config_entry,
    update_file_license, update_map,
    update_sort_order,
    get_all_logos_from_db,
    get_all_assets_from_db,
    get_files_by_type_from_db,
    synchronize_teams_with_db,
    synchronize_icons_with_db,
    get_all_teams_from_db)
from histarchexplorer.database.map import get_maps
from histarchexplorer.models.config import ConfigEntity


class EntryNotFound(Exception):
    pass


class Admin:
    class TooManyMainProjects(Exception):
        pass

    def __init__(self, fields=None) -> None:
        self.config_entities = g.config_entities
        self.config_links = g.config_links
        self.config_properties = g.config_properties
        self.config_classes = g.config_classes
        self.admin_fields = fields if fields is not None else g.admin_fields
        self.language = g.language
        self.logos = self.get_all_logo_filenames()
        self.assets = self.get_all_asset_filenames()
        self.teams = self.get_all_team_filenames()
        self.icons = self.get_files_by_type('icon')
        self.licenses = self.get_licenses()
        self.file_licenses = self.get_file_licenses()
        synchronize_teams_with_db()
        synchronize_icons_with_db()

    @staticmethod
    def get_files_by_type(file_type: str) -> list[dict[str, Any]]:
        return get_files_by_type_from_db(file_type)

    @staticmethod
    def get_licenses() -> Any:
        return get_licenses()

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
    def add_entry(data: dict[str, str | int]) -> int:
        return add_entry(data)

    @staticmethod
    def edit_entry(data: dict[str, str | int | None]) -> None:
        return update_config_entry(data)

    @staticmethod
    def add_link(data: dict[str, Any]) -> None:
        return add_link(data)

    @staticmethod
    def delete_link(id_: int) -> None:
        return delete_link(id_)

    @staticmethod
    def update_sort_order(table: str, params: list[dict[str, int]]) -> None:
        return update_sort_order(table, params)

    @staticmethod
    def check_sortorder() -> int:
        return check_sortorder()

    @staticmethod
    def get_config_class_by_id(id_: int) -> int | None:
        return get_config_class_by_id(id_)

    @staticmethod
    def delete_entry(id_: int) -> None:
        return delete_entry(id_)

    @staticmethod
    def get_maps() -> tuple[str]:
        return get_maps()

    @staticmethod
    def get_file_licenses() -> dict[str, Any]:
        return get_file_licenses()

    @staticmethod
    def add_license(spdx_id: str, uri: str, label: str, category: str) -> None:
        return add_license(spdx_id, uri, label, category)

    @staticmethod
    def delete_license(license_id: int) -> None:
        return delete_license(license_id)

    @staticmethod
    def update_file_license(
            filename: str,
            license_id: int,
            attribution: str) -> None:
        return update_file_license(filename, license_id, attribution)

    @staticmethod
    def get_all_logos_with_ids() -> list[dict[str, Any]]:
        return get_all_logos_from_db()

    @staticmethod
    def get_logo_id_to_filename_map() -> dict[int, str]:
        logo_list = Admin.get_all_logos_with_ids()
        return {logo['id']: logo['filename'] for logo in logo_list}

    @staticmethod
    def get_all_logo_filenames() -> list[str]:
        return [logo['filename'] for logo in Admin.get_all_logos_with_ids()]

    @staticmethod
    def get_all_assets_with_ids() -> list[dict[str, Any]]:
        return get_all_assets_from_db()

    @staticmethod
    def get_asset_id_to_filename_map() -> dict[int, str]:
        asset_list = Admin.get_all_assets_with_ids()
        return {asset['id']: asset['filename'] for asset in asset_list}

    @staticmethod
    def get_all_asset_filenames() -> list[str]:
        return [asset['filename'] for asset in Admin.get_all_assets_with_ids()]

    @staticmethod
    def get_all_teams_with_ids() -> list[dict[str, Any]]:
        return get_all_teams_from_db()

    @staticmethod
    def get_team_id_to_filename_map() -> dict[int, str]:
        team_list = Admin.get_all_teams_with_ids()
        return {team['id']: team['filename'] for team in team_list}

    @staticmethod
    def get_all_team_filenames() -> list[str]:
        return [team['filename'] for team in Admin.get_all_teams_with_ids()]

    def _has_translation(self, entity: ConfigEntity, field_key: str) -> bool:
        value_attr = getattr(
            entity, field_key, None)
        if isinstance(value_attr, dict) and 'display' in value_attr:
            return bool(value_attr['display'].get(self.language))
        if value_attr is not None:
            return True
        return False

    def process_entities_by_tab(
            self, tabs: list[dict[str, str]],
            entry: Optional[str]) -> dict[str, list[dict[str, Any]]]:
        result: dict[str, list[dict[str, Any]]] = {}
        for t_data in tabs:
            tab_id = t_data['id']
            tab_target = t_data['target']
            fields_for_tab = self.admin_fields.get(tab_target, [])
            filtered: list[dict[str, Any]] = []
            relevant_entities = [
                e for e in self.config_entities if e.class_id == tab_id]

            for entity in relevant_entities:
                entity_dict: dict[str, Any] = {
                    'id': entity.id,
                    'class_id': entity.class_id,
                    'license_id': entity.license_id}

                for field_config in fields_for_tab:
                    field_key = field_config['key']
                    is_trans = field_config.get('translatable', False)

                    if is_trans:
                        has_trans = self._has_translation(entity, field_key)
                    else:
                        has_trans = bool(getattr(entity, field_key, None))

                    entity_dict[
                        f"{field_key}_has_current_translation"] = has_trans

                    raw_val = getattr(entity, field_key, None)

                    if (is_trans and isinstance(raw_val, dict)
                            and 'display' in raw_val):
                        entity_dict[f"{field_key}_display_label"] = (
                            raw_val['display'].get('label', ''))
                        entity_dict[field_key] = raw_val
                    elif raw_val is not None:
                        entity_dict[f"{field_key}_display_label"] = raw_val
                        entity_dict[field_key] = raw_val
                    else:
                        entity_dict[f"{field_key}_display_label"] = ''
                        entity_dict[field_key] = None

                is_active = tab_target + str(entity.id) == entry
                entity_dict.update({
                    'is_active_entry': is_active,
                    'is_collapsed_entry': not is_active,
                    'fields_config': fields_for_tab})

                filtered.append(entity_dict)
            result[tab_target] = filtered
        return result

    def process_links_by_entity(self) -> dict[int, list[dict[str, Any]]]:
        result = defaultdict(list)
        for link in self.config_links:
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

    def process_properties_by_tab(
            self, tabs: list[dict[str, str]]
            ) -> dict[str, list[dict[str, Any]]]:
        result = {}
        for t_data in tabs:
            tab_id = t_data['id']
            tab_target = t_data['target']
            props = []
            for prop in self.config_properties:
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

    def process_roles(self) -> list[dict[str, Any]]:
        return [
            {**entity.__dict__,
             'name_display_label': entity.name['display']['label']}
            for entity in self.config_entities
            if entity.class_id == self.config_classes['attribute']]

    def process_target_nodes(self) -> list[dict[str, Any]]:
        return [
            {**entity.__dict__,
             'name_display_label': entity.name['display']['label']}
            for entity in self.config_entities]

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
