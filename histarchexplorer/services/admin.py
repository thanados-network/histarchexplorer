from typing import Any

from histarchexplorer.database.admin import (
    add_link, add_new_map, check_sortorder, create_config_entry, delete_entry,
    delete_link,
    delete_map,
    get_config_type_class_by_id, set_hidden_entities,
    set_index_background,
    set_shown_entities, update_config_entry, update_map)
from histarchexplorer.database.map import get_maps


class EntryNotFound(Exception):
    pass

class Admin:
    class TooManyMainProjects(Exception):
        pass

    @staticmethod
    def set_hidden_entities(form: list[str]) -> None:
        return set_hidden_entities(form)

    @staticmethod
    def set_shown_entities(form: list[str]) -> None:
        return set_shown_entities(form)

    @staticmethod
    def set_index_background(settings: dict[str, str]) -> None:
        return set_index_background(settings)

    @staticmethod
    def add_new_map(data: dict[str, str]) -> int:
        return add_new_map(data)

    @staticmethod
    def delete_map(map_id:int) -> None:
        return delete_map(map_id)

    @staticmethod
    def update_map(data: dict[str, str]) -> None:
        return update_map(data)

    @staticmethod
    def add_entry(data: dict) -> int:
        return create_config_entry(data)

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
    def get_config_config_types_by_id(id_: int) -> int | None:
        return get_config_type_class_by_id(id_)

    @staticmethod
    def delete_entry(id_: int) -> None:
        return delete_entry(id_)


    @staticmethod
    def get_maps() -> tuple[str]:
        return get_maps()
