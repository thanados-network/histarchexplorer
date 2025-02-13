from dataclasses import dataclass
from typing import Optional


@dataclass
class Parser:
    search: list[str] = None
    entities: list[str] = None
    linked_entities: list[str] = None
    cidoc_classes: list[str] = None
    view_classes: list[str] = None
    system_classes: list[str] = None
    type_id: list[int] = None
    show: list[str] = None
    download: bool = False
    count: bool = False
    locale: str = 'en'
    sort: str = 'asc'
    column: str = 'name'
    limit: int = 0
    first: int = None
    last: int = None
    page: int = None
    export: str = None
    format: str = 'lpx'
    relation_type: int = None
    centroid: bool = 'false'
    geometry: list[str] = None
    image_size: str = ''
    file_id: int = None
    properties: list[str] = None

    def __setattr__(
            self,
            name: str,
            value: Optional[str | list[str]] = None) -> None:
        if (name in self.__annotations__ and
                isinstance(getattr(self, name), list)):
            if getattr(self, name) is None:
                setattr(self, name, [])
            if isinstance(value, list):
                getattr(self, name).extend(value)
            else:
                getattr(self, name).append(value)
        else:
            super().__setattr__(name, value)

    def __repr__(self) -> str:
        return str(self.__dict__)
