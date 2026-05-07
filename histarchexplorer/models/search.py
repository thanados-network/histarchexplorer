import json
from typing import Any

import requests
from flask import g


class SearchService:
    """Service layer for handling search-related business logic."""

    def __init__(self, app: Any) -> None:
        self.api_url = app.config['API_URL']
        self.view_classes = g.view_classes
        self.app_logger = app.logger

    def _make_api_call(self, url: str) -> list[str]:
        """
        Internal helper to make an API call and handle responses.
        Args:
            url (str): The URL to make the GET request to.
        Returns:
            list: A list of results from the API, or an empty list on error.
        """
        try:
            response = requests.get(
                url,
                headers=g.api_headers,
                timeout=10)
            response.raise_for_status()
            data = response.json()
            results = data.get("results", [])
            return results if isinstance(results, list) else []
        except requests.exceptions.RequestException as e:
            self.app_logger.error(f"API call error to {url}: {e}")
            return []
        except json.JSONDecodeError as e:
            self.app_logger.error(f"JSON decode error from {url}: {e}")
            return []
        except Exception as e:
            self.app_logger.error(
                f"An unexpected error occurred for {url}: {e}")
            return []

    def perform_search(
            self,
            query: str,
            category: str,
            system_classes: list[str]) -> list[str]:
        """
        Performs a search based on query, category, and system classes.
        Args:
            query (str): The search query string.
            category (str): The selected category (e.g., 'all',
            'architecture').
            system_classes (list): A list of specific system classes to
            search within.
        Returns:
            list: A list of aggregated search results.
        """
        all_results = []

        if not system_classes:
            system_class_to_use = self.view_classes.get(category, ['all'])[0]
            url = f"{self.api_url}search/{system_class_to_use}?term={query}"
            all_results.extend(self._make_api_call(url))
        else:
            for sc in system_classes:
                url = f"{self.api_url}search/{sc}?term={query}"
                all_results.extend(self._make_api_call(url))
        return all_results

    def get_entity_detail(self, entity_id: int) -> dict[str, str] | None:
        """
        Fetches detailed information for a specific entity.
        Args:
            entity_id (int): The ID of the entity to fetch details for.
        Returns:
            dict: The entity's feature data, or None if not found/error.
        """
        url = f"{self.api_url}entity/{entity_id}"
        try:
            response = requests.get(
                url,
                headers=g.api_headers,
                timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get('features', [None])[0]
        except requests.exceptions.RequestException as e:
            self.app_logger.error(
                f"API call error for entity {entity_id}: {e}")
            return None
        except json.JSONDecodeError as e:
            self.app_logger.error(
                f"JSON decode error for entity {entity_id}: {e}")
            return None
        except Exception as e:
            self.app_logger.error(
                f"An unexpected error occurred for entity {entity_id}: {e}")
            return None

    def perform_live_search(
            self,
            query: str,
            system_classes: list[str]) -> list[str]:
        """
        Performs a live search (e.g., for autocomplete).
        Args:
            query (str): The search query.
            system_classes (list): List of system classes to search within.
        Returns:
            list: A list of live search results.
        """
        if len(query) < 3:
            return []

        if not system_classes:
            system_classes = ['all']

        live_results = []
        for sc in system_classes:
            api_url = f"{self.api_url}search/{sc}?term={query}"
            live_results.extend(self._make_api_call(api_url))
        return live_results
