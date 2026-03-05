import json
from pydantic import BaseModel

from histarchexplorer.database.settings import (
    create_settings_table, get_settings, save_settings)


class Settings(BaseModel):
    index_img: str = \
        '/static/images/index_map_bg/Blank_map_of_Europe_central_network.png'
    index_map: int = 1
    img_map: str = 'map'
    preferred_language: str = 'en'
    greyscale: bool = False
    darkmode: bool = False
    language_selector: bool = False
    access_restriction: bool = False
    shown_classes: list[str] = [
        'place', 'feature', 'stratigraphic_unit',
        'artifact', 'human_remains', 'person', 'group',
        'acquisition', 'event', 'activity', 'creation',
        'move', 'production', 'modification']
    shown_types: list[str] = []
    hidden_classes: list[str] = ['group']
    hidden_types: list[str] = []
    shown_ids: list[int] = []
    hidden_ids: list[int] = []
    case_study_type_id: int = 8240
    nav_logo: str = 'thanados_light.svg'
    footer_logos: list[int] = []
    legal_notice: dict[str, str] = {}
    entity_colors: dict[str, str] = {
        'places': '#23cba7',
        'actors': '#e83e8c',
        'events': '#2980b9',
        'items': '#fddb6d',
        'sources': '#5c2a36',
        'files': '#1f253d',
        'feature': '#BBBBBB',
        'stratigraphic_unit': '#000000'
    }
    available_colors: list[str] = [
        '#23cba7', '#e83e8c', '#2980b9', '#fddb6d', '#5c2a36', '#1f253d',
        '#4477AA', '#EE6677', '#228833', '#CCBB44', '#66CCEE', '#AA3377',
        '#BBBBBB', '#004488', '#DDAA33', '#BB5566', '#000000',
        '#0077BB', '#33BBEE', '#009988', '#EE7733', '#CC3311', '#EE3377',
        '#2E4053', '#5D6D7E', '#85929E', '#AEB6BF', '#D6DBDF',
        '#1A5276', '#1D8348', '#9A7D0A', '#922B21', '#633974',
        '#7E5109', '#1C2833', '#99A3A4', '#515A5A'
    ]
    menu_management: dict = {
        'start_page': {'show': True, 'page_type': 'default'},
        'legal_notice': {'show': True, 'page_type': 'default'},
        'about': {'show': True, 'page_type': 'default'},
        'publications': {'show': True, 'page_type': 'default'},
        'outcome': {'show': True, 'page_type': 'default'},
        'search': {'show': True, 'page_type': 'default'},
        'footer': {'show': True, 'page_type': 'default'},
        }

    @classmethod
    def load_from_db(cls) -> 'Settings':
        create_settings_table()

        default_settings = cls().model_dump()
        db_settings_raw = {row.key: row.value for row in get_settings()}

        default_menu = default_settings.get('menu_management', {})
        db_menu_raw = db_settings_raw.get('menu_management')
        db_menu = {}
        if isinstance(db_menu_raw, str):
            try:
                loaded_json = json.loads(db_menu_raw)
                if isinstance(loaded_json, dict):
                    db_menu = loaded_json
            except json.JSONDecodeError:
                pass
        elif isinstance(db_menu_raw, dict):
            db_menu = db_menu_raw

        merged_menu = {**default_menu, **db_menu}

        merged_settings_data = {**default_settings, **db_settings_raw}
        merged_settings_data['menu_management'] = merged_menu

        instance = cls(**merged_settings_data)
        instance.save_to_db()

        return instance

    def save_to_db(self):
        for key, value in self.model_dump().items():
            save_settings(key, value)

    def get_map_settings(self) -> dict:
        return {
            'img': self.index_img,
            'map': self.index_map,
            'img_map': self.img_map,
            'greyscale': self.greyscale}
