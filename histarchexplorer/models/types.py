from typing import Any


class Types:
    def __init__(self, data: dict[str, Any]):
        self.label = data.get('label')
        self.hierarchy = data.get('hierarchy')
        self.value = data.get('value')
        self.unit = data.get('unit')
        self.description = data.get('descriptions')
        self.id = data.get('identifier').rsplit('/', 1)[-1]
        self.url = data.get('identifier')
        self.root = self.hierarchy.split('>')[0].rstrip()
        self.type_hierarchy = data.get('typeHierarchy')

    def __repr__(self) -> str:
        return str(self.__dict__)
