from typing import Any, Optional

from flask import g, url_for


class Depiction:
    def __init__(self, data: dict[str, Any], entity_id: int) -> None:
        self.id_ = int(data['@id'].rsplit('/', 1)[-1])
        self.link = data.get('@id')
        self.title = data.get('title')
        self.license = data.get('license')
        self.license_holder = data.get('licenseHolder')
        self.creator = data.get('creator')
        self.url = data.get('url')
        self.mimetype = data.get('mimetype')
        self.iiif_manifest = self.format_manifest_url(data.get('IIIFManifest'))
        self.iiif_base_path = data.get('IIIFBasePath')
        self.entity_id = entity_id
        self.main_image = self.check_if_main_image()

    def __repr__(self) -> str:  # pragma: no cover
        return str(self.__dict__)

    def check_if_main_image(self) -> bool:
        if g.main_images.get(self.entity_id):
            if g.main_images.get(self.entity_id) == self.id_:
                return True
        return False

    @staticmethod
    def format_manifest_url(manifest_url: Optional[str]) -> str:
        url = ''
        if manifest_url:
            url = f'{manifest_url}?url={url_for("index", _external=True)}'
        return url
