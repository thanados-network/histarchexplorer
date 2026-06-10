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
        """Fetch the number of entities grouped by system class.

        Queries the external API using the provided parser parameters and
        returns a dictionary mapping class names to their total counts.
        """
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
        """Get entities count statistics filtered by case study type IDs.

        Queries class counts, defaulting to the globally configured case
        study IDs. Results are memoized for performance.
        """
        parser = Parser(type_id=type_ids or g.case_study_ids)
        return ApiAccess.get_system_class_count(parser)

    @staticmethod
    @cache.memoize()
    def get_files_of_entities() -> dict[str, Any]:
        """Retrieve all file-to-entity mappings from the external API.

        Fetches media relationships. Results are memoized to reduce
        network overhead.
        """
        return requests.get(
            f"{app.config['API_URL']}/files_of_entities/",
            headers=g.api_headers,
            proxies=PROXIES,
            timeout=60).json()

    @staticmethod
    @cache.memoize()
    def get_type_tree() -> dict[str, Any]:
        """Fetch the full hierarchical type tree categorized by view class.

        Queries the API endpoints. Results are memoized for faster
        subsequent lookups.
        """
        return requests.get(
            f"{app.config['API_URL']}/type_by_view_class/",
            headers=g.api_headers,
            timeout=20).json()

    @staticmethod
    def get_by_system_class(
            class_: str,
            parser: Parser) -> list[dict[str, Any]]:
        """Query and return all entities belonging to a specific system class.

        Retrieves a list of matching entity objects from the system class
        endpoint using the given parser parameters.
        """
        req = requests.get(
            f"{app.config['API_URL']}system_class/{class_}",
            params=parser.__dict__,
            proxies=PROXIES,
            timeout=60).json()
        return req['results']

