from dataclasses import dataclass


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
    download: bool = None
    count: bool = None
    locale: str = None
    sort: str = None
    column: str = None
    limit: int = None
    first: int = None
    last: int = None
    page: int = None
    export: str = None
    format: str = None
    relation_type: int = None
    centroid: bool = None
    geometry: list[str] = None
    image_size: str = None
    file_id: int = None
    properties: list[str] = None

    def __setattr__(self, name, value):
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
