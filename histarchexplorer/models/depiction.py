from typing import Any


class Depiction:
    def __init__(self, data: dict[str, Any]):
        self.link = data.get('@id')
        self.title = data.get('title')
        self.license = data.get('license')
        self.url = data.get('url')
        self.mimetype = data.get('mimetype')
        self.iiif_manifest = data.get('IIIFManifest')

    def __repr__(self) -> str:
        return str(self.__dict__)
