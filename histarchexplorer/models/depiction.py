from typing import Any

from flask import g


class Depiction:
    def __init__(self, data: dict[str, Any], entity_id:int) -> None:
        self.id_ = int(data['@id'].rsplit('/', 1)[-1])
        self.link = data.get('@id')
        self.title = data.get('title')
        self.license = data.get('license')
        self.url = data.get('url')
        self.mimetype = data.get('mimetype')
        self.iiif_manifest = data.get('IIIFManifest')
        self.entity_id = entity_id
        self.main_image = self.check_if_main_image()

    def __repr__(self) -> str:
        return str(self.__dict__)

    def check_if_main_image(self) -> bool:
        if g.main_images.get(self.entity_id):
            if g.main_images.get(self.entity_id) == self.id_:
                return True
        return False
