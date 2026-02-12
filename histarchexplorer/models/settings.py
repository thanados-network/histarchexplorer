from pydantic import BaseModel
from typing import List

from histarchexplorer.database.settings import (
    create_settings_table, get_settings, save_settings, set_default_settings)


class Settings(BaseModel):
    index_img: str = '/static/images/index_map_bg/Blank_map_of_Europe_central_network.png'
    index_map: int = 1
    img_map: str = 'map'
    greyscale: bool = False
    darkmode: bool = False
    language_selector: bool = False
    access_restriction: bool = False
    shown_classes: List[str] = ['place', 'feature', 'stratigraphic_unit', 'artifact', 'human_remains', 'person', 'group', 'acquisition', 'event', 'activity', 'creation', 'move', 'production', 'modification']
    shown_types: List[str] = []
    hidden_classes: List[str] = ['group']
    hidden_types: List[str] = []
    shown_ids: List[int] = []
    hidden_ids: List[int] = []
    case_study_type_id: int = 8240

    @classmethod
    def load_from_db(cls) -> 'Settings':
        create_settings_table()

        for key, value in cls().model_dump().items():
            set_default_settings(key, value)

        return cls(**{row.key: row.value for row in get_settings()})

    def save_to_db(self):
        for key, value in self.model_dump().items():
            save_settings(key, value)

    def get_map_settings(self) -> dict:
        return {
            'img': self.index_img,
            'map': self.index_map,
            'img_map': self.img_map,
            'greyscale': self.greyscale}

