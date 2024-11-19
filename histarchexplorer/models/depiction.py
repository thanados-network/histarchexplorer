from typing import Any

from flask import g

import requests


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
        self.iiif_manifest = data.get('IIIFManifest')
        self.entity_id = entity_id
        self.main_image = self.check_if_main_image()
        self.iiif_image_url = self.get_iiif_image_url()


    def get_iiif_image_url(self):
        if self.iiif_manifest:
            response = requests.get(self.iiif_manifest)
            if response.status_code == 200:
                manifest_data = response.json() #to python dict
                if 'sequences' in manifest_data:
                    for sequence in manifest_data['sequences']:
                        for canvas in sequence['canvases']:
                            if 'images' in canvas:
                                for image in canvas['images']:
                                    if 'resource' in image:
                                        image_url = image['resource']['@id']
                                        full_image_url = f"{image_url}/full/max/0/default.jpg"
                                        return full_image_url
        return None

    def __repr__(self) -> str:
        return str(self.__dict__)

    def check_if_main_image(self) -> bool:
        if g.main_images.get(self.entity_id):
            if g.main_images.get(self.entity_id) == self.id_:
                return True
        return False
