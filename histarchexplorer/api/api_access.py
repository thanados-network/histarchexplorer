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
    def _api_v1_base() -> str:
        base = app.config['API_URL'].rstrip('/')
        if not base.endswith('/1'):
            base += '/1'
        return base

    @staticmethod
    def _get_vocabulary(endpoint: str) -> dict[str, Any]:
        """Fetch a fixed versioned vocabulary endpoint, rejecting bad data."""
        response = requests.get(
            f'{ApiAccess._api_v1_base()}/vocabulary/{endpoint}',
            headers=g.api_headers,
            proxies=PROXIES,
            timeout=60)
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict):
            raise ValueError('Invalid vocabulary payload')
        return payload

    @staticmethod
    @cache.memoize()
    def get_vocabulary_tree() -> dict[str, Any]:
        """Return the unchanged vocabulary tree from the shared cache."""
        return ApiAccess._get_vocabulary('tree')

    @staticmethod
    @cache.memoize()
    def get_vocabulary_detail(id_: int) -> dict[str, Any]:
        """Return the unchanged detail of a positive vocabulary type ID."""
        if type(id_) is not int or id_ <= 0:
            raise ValueError('Vocabulary IDs must be positive integers')
        return ApiAccess._get_vocabulary(str(id_))

    @staticmethod
    def _normalize_case_study_ids(
            case_studies: int | list[int] | tuple[int, ...] | None
    ) -> tuple[int, ...]:
        raw: Any = (
            case_studies if case_studies
            else getattr(g, 'case_study_ids', None) or ())
        if isinstance(raw, int) and not isinstance(raw, bool):
            return (raw,) if raw > 0 else ()
        seen: list[int] = []
        for item in raw:
            if (isinstance(item, int) and not isinstance(item, bool)
                    and item > 0 and item not in seen):
                seen.append(item)
        return tuple(seen)

    @staticmethod
    @cache.memoize()
    def get_system_class_count(
            case_studies: tuple[int, ...] = ()) -> dict[str, int]:
        """Fetch entity counts grouped by system class via API v1."""
        params: dict[str, Any] = (
            {'caseStudy': list(case_studies)} if case_studies else {})
        response = requests.get(
            f'{ApiAccess._api_v1_base()}/system/count/entities',
            params=params,
            headers=getattr(g, 'api_headers', {}),
            proxies=PROXIES,
            timeout=30)
        response.raise_for_status()
        payload = response.json()
        if (not isinstance(payload, dict)
                or not isinstance(payload.get('counts'), dict)):
            raise ValueError('Invalid entity counts payload')
        return {
            str(cls_name): int(count)
            for cls_name, count in payload['counts'].items()}

    @staticmethod
    def get_entities_count_by_case_studies(
            type_ids: int | list[int] | tuple[int, ...] | None = None
    ) -> dict[str, int]:
        """Get entity counts filtered by case study IDs.

        Defaults to globally configured ``g.case_study_ids``. Cached via
        ``get_system_class_count`` keyed by normalized ID tuples.
        """
        normalized = ApiAccess._normalize_case_study_ids(type_ids)
        return ApiAccess.get_system_class_count(normalized)

    @staticmethod
    @cache.memoize()
    def get_files_of_entities() -> dict[str, Any]:
        """Retrieve all file-to-entity mappings from the external API.

        Fetches media relationships. Results are memoized to reduce
        network overhead.

        Returns:
            dict[str, list[dict[str, Any]]]: Dict mapping "files" to a list of
                file dictionaries. Each file dictionary contains:
                - id (int): File ID.
                - title (str): Title or filename.
                - mimetype (str): File MIME type.
                - license (str): License identifier.
                - publicShareable (bool): Shareability flag.
        """
        return requests.get(
            f"{app.config['API_URL']}files_of_entities/",
            headers=g.api_headers,
            proxies=PROXIES,
            timeout=60).json()

    @staticmethod
    @cache.memoize()
    def get_type_tree() -> dict[str, Any]:
        """Fetch the full hierarchical type tree categorized by view class.

        Queries the API endpoints. Results are memoized for faster
        subsequent lookups.

        Returns:
            dict[str, list[dict[str, Any]]]: A dictionary mapping categories
                (e.g., "case_study") to a list of types. Each type dict
                contains:
                - id (int): Unique classification type ID.
                - title (str): Type title.
                - typeHierarchy (list[dict]): Parent hierarchy entry dicts with
                  keys: 'identifier', 'label', 'descriptions'.
                - isStandard (bool): Whether it is a standard system type.
        """
        return requests.get(
            f"{app.config['API_URL']}type_by_view_class/",
            headers=g.api_headers,
            proxies=PROXIES,
            timeout=20).json()

    @staticmethod
    @cache.memoize()
    def get_subunits(id_: int) -> dict[str, Any]:
        """Fetch the complete ordered hierarchy below an entity.

        The response is expected to contain feature, stratigraphic-unit,
        artifact, and human-remains cards with their display metadata.
        """
        response = requests.get(
            f"{app.config['API_URL']}subunits/{id_}",
            headers=g.api_headers,
            proxies=PROXIES,
            timeout=60)
        response.raise_for_status()
        return response.json()

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

    @staticmethod
    def get_table_rows(
            classes: list[str],
            table_columns: Optional[list[str]] = None,
            limit: int = 0) -> dict[str, Any]:
        """Fetch tabular data for specific classes and columns from the API.

        Queries the OpenAtlas API table_rows endpoint.
        """
        # TODO: Once a dedicated endpoint for external reference systems is
        # available in the OpenAtlas API, replace the get_table_rows quickfix
        # with the new endpoint.
        if table_columns is None:
            table_columns = ['name']
        params = {
            'system_classes': classes,
            'table_columns': table_columns,
            'limit': limit}
        return requests.get(
            f"{app.config['API_URL']}table_rows/",
            params=params,
            headers=g.api_headers,
            proxies=PROXIES,
            timeout=30).json()

    @staticmethod
    @cache.memoize()
    def get_case_studies() -> list[dict[str, Any]]:
        """Fetch the hierarchical list of case studies via API v1."""
        response = requests.get(
            f'{ApiAccess._api_v1_base()}/case-studies',
            headers=getattr(g, 'api_headers', {}),
            proxies=PROXIES,
            timeout=30)
        response.raise_for_status()
        payload = response.json()
        if (not isinstance(payload, dict)
                or not isinstance(payload.get('data'), list)):
            raise ValueError('Invalid case studies payload')
        return payload['data']

    @staticmethod
    def get_case_study(id_: int) -> dict[str, Any] | None:
        """Fetch metadata for a single case study via API v1."""
        if type(id_) is not int or id_ <= 0:
            raise ValueError('Case study IDs must be positive integers')
        response = requests.get(
            f'{ApiAccess._api_v1_base()}/case-studies/{id_}',
            headers=getattr(g, 'api_headers', {}),
            proxies=PROXIES,
            timeout=30)
        if response.status_code == 404:
            return None
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict) or 'id' not in payload:
            raise ValueError('Invalid case study payload')
        return payload

    @staticmethod
    def get_type_descendant_ids(ids: list[int]) -> list[int]:
        """Expand type IDs with all descendants via vocabulary tree."""
        if not ids:
            return []
        target_ids = [
            int(i) for i in ids
            if isinstance(i, int) and not isinstance(i, bool)]
        if not target_ids:
            return []

        dedup_targets = list(dict.fromkeys(target_ids))
        try:
            tree = ApiAccess.get_vocabulary_tree()
        except (requests.RequestException, ValueError):
            return dedup_targets

        node_by_id: dict[int, dict[str, Any]] = {}

        def index_nodes(nodes: list[Any]) -> None:
            for node in nodes:
                if not isinstance(node, dict):
                    continue
                raw_id = node.get('id')
                if (isinstance(raw_id, int)
                        and not isinstance(raw_id, bool) and raw_id > 0):
                    node_by_id[raw_id] = node
                children = node.get('children')
                if isinstance(children, list) and children:
                    index_nodes(children)

        for items in tree.values():
            if isinstance(items, list):
                index_nodes(items)

        result: list[int] = []
        seen: set[int] = set()

        def collect_subtree(node: dict[str, Any]) -> None:
            raw_id = node.get('id')
            if (isinstance(raw_id, int)
                    and not isinstance(raw_id, bool)
                    and raw_id > 0 and raw_id not in seen):
                seen.add(raw_id)
                result.append(raw_id)
            children = node.get('children')
            if isinstance(children, list):
                for child in children:
                    if isinstance(child, dict):
                        collect_subtree(child)

        for tid in target_ids:
            if tid in node_by_id:
                collect_subtree(node_by_id[tid])
            elif tid not in seen:
                seen.add(tid)
                result.append(tid)
        return result

    @staticmethod
    def get_p46_child_ids(id_: int) -> list[int]:
        """Return direct P46 child IDs from the subunits API endpoint."""
        if type(id_) is not int or id_ <= 0:
            return []
        try:
            payload = ApiAccess.get_subunits(id_)
        except (requests.RequestException, ValueError):
            return []

        if not isinstance(payload, dict):
            return []
        nodes = payload.get(str(id_))
        if not isinstance(nodes, list):
            return []

        for node in nodes:
            if isinstance(node, dict) and node.get('id') == id_:
                raw_children = node.get('children') or []
                if not isinstance(raw_children, list):
                    return []
                children: list[int] = []
                for cid in raw_children:
                    if (isinstance(cid, int)
                            and not isinstance(cid, bool)
                            and cid not in children):
                        children.append(cid)
                return children
        return []

    @staticmethod
    @cache.memoize()
    def get_map_overlays() -> list[dict[str, Any]]:
        """Fetch all paginated map overlays via OpenAtlas API v1."""
        overlays: list[dict[str, Any]] = []
        seen_ids: set[int] = set()
        page = 1
        max_pages = 1000
        base = ApiAccess._api_v1_base()
        headers = getattr(g, 'api_headers', {})

        while page <= max_pages:
            response = requests.get(
                f'{base}/files/overlays',
                params={'limit': 100, 'page': page},
                headers=headers,
                proxies=PROXIES,
                timeout=30)
            response.raise_for_status()
            payload = response.json()
            if (not isinstance(payload, dict)
                    or not isinstance(payload.get('data'), list)):
                raise ValueError('Invalid map overlays payload')

            data = payload['data']
            if not data:
                break

            for item in data:
                if not isinstance(item, dict):
                    continue
                raw_id = item.get('id')
                if type(raw_id) is not int or raw_id in seen_ids:
                    continue
                bounds = item.get('bounds')
                if not isinstance(bounds, list) or len(bounds) < 2:
                    continue
                seen_ids.add(raw_id)
                overlays.append({
                    'id': raw_id,
                    'name': item.get('name') or '',
                    'bbox': bounds,
                    'iiif_base_url': item.get('iiifBaseUrl'),
                    'extension': item.get('extension'),
                    'file_url': item.get('fileUrl')})

            if not payload.get('next'):
                break
            page += 1

        return overlays

