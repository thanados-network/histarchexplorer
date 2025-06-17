from typing import Any

from flask import g


class Types:
    def __init__(self, data: dict[str, Any]):
        self.label = data.get('label')
        self.hierarchy = data['hierarchy']
        self.value = data.get('value')
        self.unit = data.get('unit')
        self.description = data.get('descriptions')
        self.id = data['identifier'].rsplit('/', 1)[-1]
        self.url = data.get('identifier')
        self.root = self.hierarchy.split('>')[0].rstrip()
        self.type_hierarchy = data['typeHierarchy']
        self.icon = self.get_icon()
        self.division = self.get_divisions()

    def __repr__(self) -> str:  # pragma: no cover
        return str(self.__dict__)

    def to_serializable(self: Any) -> Any:
        if isinstance(self, list):
            return [Types.to_serializable(item) for item in self]
        elif hasattr(self, "__dict__"):
            return {
                key: Types.to_serializable(value)
                for key, value in self.__dict__.items()}
        elif isinstance(self, dict):
            return {
                key: Types.to_serializable(value)
                for key, value in self.items()}
        return self

    def get_icon(self) -> str:
        icon = g.sidebar_icons.get(int(self.id))
        if not icon:
            for type_ in self.type_hierarchy:
                type_id = int(type_['identifier'].rsplit('/', 1)[-1])
                if g.sidebar_icons.get(type_id):
                    icon = g.sidebar_icons.get(type_id)
                    break
        return icon or g.sidebar_icons.get('other')

    def get_divisions(self) -> dict[str, str]:
        division = g.type_divisions.get(int(self.id))
        if not division:
            for type_ in self.type_hierarchy:
                type_id = int(type_['identifier'].rsplit('/', 1)[-1])
                if g.type_divisions.get(type_id):
                    division = g.type_divisions.get(type_id)
                    break

        return division or {'label': 'other', 'icon': '<i class="bi bi-boxes"></i>'}

