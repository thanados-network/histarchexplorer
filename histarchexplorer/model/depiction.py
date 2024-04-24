import os
from typing import Any


class Depiction:
    def __init__(self, data: dict[str, Any]):
        self.link = data['@id']
        self.title = data['title']
        self.license = data['license']
        self.url = data['url']
        self.extension = os.path.splitext(self.url.rsplit('/', 1)[-1])[1]
