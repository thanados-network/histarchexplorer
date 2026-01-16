from dataclasses import dataclass

from histarchexplorer.database.settings import get_settings


@dataclass
class Settings:
    id: int
    index_img: str
    index_map: int
    img_map: str
    greyscale: bool
    shown_classes: list[str]
    shown_types: list[str]
    hidden_classes: list[str]
    hidden_types: list[str]
    shown_ids: list[str]
    hidden_ids: list[str]
    case_study_type_id: int

    @classmethod
    def initialize_settings(cls) -> "Settings":
        return cls(**get_settings()._asdict())

    def get_map_settings(self) -> dict[str, str | int]:
        return {
            'img': self.index_img,
            'map': self.index_map,
            'img_map': self.img_map,
            'greyscale': self.greyscale}
