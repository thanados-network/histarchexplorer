from typing import Any, Optional

import requests
from flask import g

from histarchexplorer import app, cache
from histarchexplorer.api.parser import Parser

PROXIES = {
    "http": app.config['API_PROXY'],
    "https": app.config['API_PROXY']}


class ApiAccess:

    @staticmethod
    def get_system_class_count(parser: Parser) -> dict[str, Any]:
        return requests.get(
            f"{app.config['API_URL']}/system_class_count/",
            params=parser.__dict__,
            headers=g.api_headers,
            proxies=PROXIES,
            timeout=30).json()

    @staticmethod
    @cache.memoize()
    def get_entities_count_by_case_studies(
            type_ids: Optional[list[int]] = None) -> dict[str, Any]:
        parser = Parser(type_id=type_ids or g.case_study_ids)
        return ApiAccess.get_system_class_count(parser)

    @staticmethod
    @cache.memoize()
    def get_files_of_entities() -> dict[str, Any]:
        return requests.get(
            f"{app.config['API_URL']}/files_of_entities/",
            headers=g.api_headers,
            proxies=PROXIES,
            timeout=60).json()

    @staticmethod
    @cache.memoize()
    def get_type_tree() -> dict[str, Any]:
        return requests.get(
            f"{app.config['API_URL']}/type_by_view_class/",
            headers=g.api_headers,
            timeout=20).json()

    @staticmethod
    @cache.memoize()
    def get_type_tree_overview() -> dict[str, Any]:
        return requests.get(
            f"{app.config['API_URL']}/type_overview/",
            headers=g.api_headers,
            timeout=20).json()

    @staticmethod
    def get_by_system_class(
            class_: str,
            parser: Parser) -> list[dict[str, Any]]:
        req = requests.get(
            f"{app.config['API_URL']}system_class/{class_}",
            params=parser.__dict__,
            proxies=PROXIES,
            timeout=60).json()
        return req['results']

    # @staticmethod
    # def get_entity(id_: int, parser: Parser) -> dict[str, Any]:
    #     req = requests.get(
    #         f"{app.config['API_URL']}entity/{id_}",
    #         params=parser.__dict__,
    #         headers=g.api_headers,
    #         proxies=PROXIES,
    #         timeout=60).json()
    #     return req

    # @staticmethod
    # def get_by_system_class(
    #         class_: str,
    #         parser: Parser) -> list[dict[str, Any]]:
    #     req = requests.get(
    #         f"{app.config['API_URL']}system_class/{class_}",
    #         params=parser.__dict__,
    #         proxies=PROXIES,
    #         timeout=60).json()
    #     return req['results']
    #
    # @staticmethod
    # def get_entities_linked_to_entity(
    #         id_: int,
    #         parser: Parser) -> list[dict[str, Any]]:
    #     url = f"{app.config['API_URL']}/entities_linked_to_entity/"
    #     return requests.get(
    #         f"{url}{id_}",
    #         params=parser.__dict__,
    #         proxies=PROXIES,
    #         timeout=30).json()['results']

    # @staticmethod
    # def linked_entities_by_properties_recursive(
    #         id_: int,
    #         parser: Parser) -> list[dict[str, Any]]:
    #     url = (f"{app.config['API_URL']}"
    #            f"/linked_entities_by_properties_recursive/")
    #     return requests.get(
    #         f"{url}{id_}",
    #         params=parser.__dict__,
    #         headers=g.api_headers,
    #         proxies=PROXIES,
    #         timeout=30).json()['results']

    # @staticmethod
    # def get_subunits(
    #         id_: int,
    #         parser: Parser) -> list[dict[str, Any]]:
    #     url = f"{app.config['API_URL']}/subunits/"
    #     return requests.get(
    #         f"{url}{id_}",
    #         params=parser.__dict__,
    #         proxies=PROXIES,
    #         timeout=30).json()


