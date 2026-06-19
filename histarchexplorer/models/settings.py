import json
from typing import Any, Dict, List, Union

from pydantic import BaseModel, Field, TypeAdapter
from pydantic_core import PydanticUndefined

from histarchexplorer.database.settings import (
    create_settings_table, get_settings, save_settings)


def _migrate_type_divisions(
        data: Dict[str, Any]) -> Dict[
    str, Dict[str, Union[str, List[int], None]]]:
    """Migrate legacy type divisions format to the newer schema.

    Translates old structure structures into named category division
    schemas with associated ids, ensuring compatibility.
    """
    if not data or not isinstance(data, dict):
        return {}

    # Check if migration is needed by inspecting the first key
    first_key = next(iter(data))
    if first_key.isdigit():
        new_data = {}
        for id_str, values in data.items():
            if not isinstance(values, dict): continue
            label = values.get('label')
            if not label: continue

            if label not in new_data:
                new_data[label] = {
                    'icon_type': values.get('icon_type'),
                    'icon_value': values.get('icon_value'),
                    'ids': []}
            new_data[label]['ids'].append(int(id_str))
        return new_data
    return data


class Settings(BaseModel):
    """Central settings data model representing application configurations.

    Contains configurations for map imagery, grey/dark modes, visible and
    hidden historical classes/types, preferred and available languages,
    color palettes, menu configurations, and division/icon mapping.
    """
    index_img: str = \
        '/static/images/index_map_bg/Blank_map_of_Europe_central_network.png'
    index_map: int = 1
    img_map: str = 'map'
    preferred_language: str = 'en'
    selected_languages: list[str] = ['en', 'de']
    language_selector: bool = False
    greyscale: bool = False
    darkmode: bool = False
    access_restriction: bool = False
    shown_classes: list[str] = [
        'place', 'feature', 'stratigraphic_unit',
        'artifact', 'human_remains', 'person', 'group',
        'acquisition', 'event', 'activity', 'creation',
        'move', 'production', 'modification', 'type',
        'source', 'file']
    shown_types: list[int] = []
    hidden_classes: list[str] = []
    hidden_types: list[int] = []
    shown_ids: list[int] = []
    hidden_ids: list[int] = []
    case_study_type_id: int = 8240
    nav_logo: str = 'thanados_light.svg'
    footer_logos: list[int] = []
    publication_types: list[str] = [
        'Works', 'Article', 'Software', 'Award', 'Press']
    legal_notice: dict[str, str] = {}
    entity_colors: dict[str, str] = {
        'places': '#23cba7',
        'actors': '#e83e8c',
        'events': '#2980b9',
        'items': '#fddb6d',
        'sources': '#5c2a36',
        'files': '#1f253d',
        'feature': '#BBBBBB',
        'stratigraphic_unit': '#000000',
        'types': '#4477AA'}
    available_colors: list[str] = [
        '#23cba7', '#e83e8c', '#2980b9', '#fddb6d', '#5c2a36', '#1f253d',
        '#4477AA', '#EE6677', '#228833', '#CCBB44', '#66CCEE', '#AA3377',
        '#BBBBBB', '#004488', '#DDAA33', '#BB5566', '#000000',
        '#0077BB', '#33BBEE', '#009988', '#EE7733', '#CC3311', '#EE3377',
        '#2E4053', '#5D6D7E', '#85929E', '#AEB6BF', '#D6DBDF',
        '#1A5276', '#1D8348', '#9A7D0A', '#922B21', '#633974',
        '#7E5109', '#1C2833', '#99A3A4', '#515A5A']
    menu_management: dict = {
        'start_page': {'show': True, 'page_type': 'default'},
        'legal_notice': {'show': True, 'page_type': 'default'},
        'about': {'show': True, 'page_type': 'default'},
        'publications': {'show': True, 'page_type': 'default'},
        'outcome': {'show': True, 'page_type': 'default'},
        'search': {'show': True, 'page_type': 'default'},
        'footer': {'show': True, 'page_type': 'default'}}
    type_divisions: Dict[str, Dict[str, Union[str, List[int], None]]] = Field(
        default_factory=lambda: {
            'administrative unit': {'icon_type': 'css',
                                    'icon_value': 'bi bi-map',
                                    'ids': [86]},
            'dimensions': {'icon_type': 'css', 'icon_value': 'bi bi-rulers',
                           'ids': [15678]},
            'anthropology': {'icon_type': 'img', 'icon_value': 'bone.svg',
                             'ids': [218963, 213216, 119444, 119334]},
            'material': {'icon_type': 'img', 'icon_value': 'material.svg',
                         'ids': [21160]},
            'age': {'icon_type': 'css',
                    'icon_value': 'bi bi-calendar-range',
                    'ids': [22277, 117198]},
            'burial characteristics': {'icon_type': None, 'icon_value': None,
                                       'ids': [213223]},
            'grave characteristics': {'icon_type': 'img',
                                      'icon_value': 'grave.svg',
                                      'ids': [218839]},
            'position of find in grave': {'icon_type': 'css',
                                          'icon_value': 'bi bi-crosshair',
                                          'ids': [23440]},
            'case study': {'icon_type': 'css', 'icon_value': 'bi bi-house',
                           'ids': [8240]}})

    @classmethod
    def load_from_db(cls) -> 'Settings':
        """Load and merge settings configurations from the database.

        Initializes the settings table if missing, reads keys, merges database
        overrides with standard default settings, handles migration and
        sanitization, and returns the active Settings instance.
        """
        create_settings_table()
        default_settings = cls().model_dump()
        db_settings_raw = {row['key']: row['value'] for row in get_settings()}

        merged_settings_data = {**default_settings, **db_settings_raw}

        for key in ['menu_management', 'type_divisions']:
            default_val = default_settings.get(key, {})
            db_val_raw = db_settings_raw.get(key)
            db_val = {}

            if isinstance(db_val_raw, str):
                try:
                    loaded_json = json.loads(db_val_raw)
                    if isinstance(loaded_json, dict):
                        db_val = loaded_json
                except json.JSONDecodeError:
                    pass
            elif isinstance(db_val_raw, dict):
                db_val = db_val_raw

            if key == 'type_divisions':
                db_val = _migrate_type_divisions(db_val)

            merged_settings_data[key] = {**default_val, **db_val}

        merged_settings_data = _validate_and_sanitize_settings(
            merged_settings_data)

        instance = cls(**merged_settings_data)
        instance.save_to_db()
        return instance

    def save_to_db(self) -> None:
        """Persist all current setting values to the database.

        Dumps setting attributes and writes them as key-value pairs into the
        database's settings table.
        """
        for key, value in self.model_dump().items():
            save_settings(key, value)

    def get_map_settings(self) -> dict[str, Any]:
        """Fetch map-specific display configuration as a dictionary.

        Returns index image path, index map identifier, image map,
        and greyscale status.
        """
        return {
            'img': self.index_img,
            'map': self.index_map,
            'img_map': self.img_map,
            'greyscale': self.greyscale}


def _validate_and_sanitize_settings(
        data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and clean settings dictionary against settings schema.

    Ensures all keys have appropriate types, list formatting, and falls back
    to default settings values on invalid data or validation failures.
    """
    sanitized = {}
    for name, field in Settings.model_fields.items():
        if field.default is not PydanticUndefined:
            default_val = field.default
        elif field.default_factory is not None:
            default_val = field.default_factory()
        else:
            default_val = None

        if name not in data:
            sanitized[name] = default_val
            continue

        v = data[name]
        origin = getattr(field.annotation, '__origin__', None)

        if field.annotation is int:
            if isinstance(v, list):
                v = v[0] if len(v) > 0 else default_val
            elif isinstance(v, str):
                try:
                    parsed = json.loads(v)
                    if isinstance(parsed, list):
                        v = parsed[0] if len(parsed) > 0 else default_val
                except Exception:
                    pass

        is_list_type = (origin is list or field.annotation is list)
        if is_list_type and v is not None and not isinstance(v, list):
            v = [v]

        try:
            adapter = TypeAdapter(field.annotation)
            validated_val = adapter.validate_python(v)
            sanitized[name] = validated_val
        except Exception:
            sanitized[name] = default_val

    return sanitized
