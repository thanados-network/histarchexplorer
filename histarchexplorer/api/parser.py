from dataclasses import dataclass
from typing import Optional


# pylint: disable=too-many-instance-attributes
@dataclass
class Parser:
    search: list[str] | None = None
    entities: list[str] | None = None
    linked_entities: list[str] | None = None
    cidoc_classes: list[str] | None = None
    view_classes: list[str] | None = None
    system_classes: list[str] | None = None
    type_id: list[int] | None = None
    show: list[str] | None = None
    first: int | None = None
    last: int | None = None
    page: int | None = None
    export: str | None = None
    relation_type: int | None = None
    geometry: list[str] | None = None
    file_id: int | None = None
    properties: list[str] | None = None
    download: bool = False
    count: bool = False
    locale: str = 'en'
    sort: str = 'asc'
    column: str = 'name'
    limit: int = 0
    format: str = 'lpx'
    centroid: str = 'false'
    image_size: str = ''

    def __setattr__(
            self,
            name: str,
            value: Optional[str | list[str]] = None) -> None: # pragma: no cover
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

    def __repr__(self) -> str:  # pragma: no cover
        return str(self.__dict__)
