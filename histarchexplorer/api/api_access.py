from typing import Any

import requests

from histarchexplorer import app

PROXIES = {
    "http": app.config['API_PROXY'],
    "https": app.config['API_PROXY']}


class ApiAccess:

    @staticmethod
    def get_entity(id_: int) -> dict[str, Any]:
        req = requests.get(
            f"{app.config['API_URL']}entity/{id_}",
            proxies=PROXIES,
            timeout=60).json()
        return req

    @staticmethod
    def get_by_system_class(class_: str) -> list[dict[str, Any]]:
        req = requests.get(
            f"{app.config['API_URL']}system_class/{class_}",
            params={'limit': 0, 'show': 'none'},
            proxies=PROXIES,
            timeout=60).json()
        return req['results']
