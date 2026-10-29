"""Search service layer communicating with the OpenAtlas v1 search API."""
from concurrent.futures import ThreadPoolExecutor
import json
import re
from typing import Any

from flask import g
import requests

OPENATLAS_SEARCH_CLASSES: tuple[str, ...] = (
    'acquisition',
    'activity',
    'artifact',
    'bibliography',
    'edition',
    'external_reference',
    'feature',
    'file',
    'group',
    'human_remains',
    'modification',
    'move',
    'person',
    'place',
    'production',
    'reference_system',
    'source',
    'stratigraphic_unit',
    'text',
    'type')

VALID_SORT_BY: frozenset[str] = frozenset({'name', 'start_date', 'end_date'})
VALID_SORT_ORDER: frozenset[str] = frozenset({'asc', 'desc'})
DATE_PARAM_RE = re.compile(r'^-?\d{1,5}(-\d{2}(-\d{2})?)?$')


def format_iso_year(iso_str: str | None) -> str:
    """Extract a human-readable year (e.g. '800' or '500 BC') from ISO date."""
    if not iso_str or not isinstance(iso_str, str):
        return ''
    text = iso_str.strip()
    is_bce = text.startswith('-')
    if is_bce:
        text = text[1:]
    year_part = text.split('-', 1)[0]
    if not year_part.isdigit():
        return ''
    year_num = int(year_part)
    if year_num == 0:
        return ''
    return f'{year_num} BC' if is_bce else str(year_num)


def _format_bound(bound: dict[str, Any] | None) -> str:
    """Format a start or end DateModel object into a concise year string."""
    if not isinstance(bound, dict):
        return ''
    earliest = format_iso_year(bound.get('earliest'))
    latest = format_iso_year(bound.get('latest'))
    if earliest and latest and earliest != latest:
        val = f'{earliest}/{latest}'
    else:
        val = earliest or latest
    comment = (bound.get('comment') or '').strip()
    if val and comment and not comment.lstrip('-').isdigit():
        return f'{comment} {val}'.strip()
    return val


def format_search_timespan(timespan: dict[str, Any] | None) -> str:
    """Format an OpenAtlas v1 TimeSpan dict into a readable range string."""
    if not isinstance(timespan, dict):
        return ''
    start_str = _format_bound(timespan.get('start'))
    end_str = _format_bound(timespan.get('end'))
    if start_str and end_str:
        if start_str == end_str:
            return start_str
        return f'{start_str} – {end_str}'
    return start_str or end_str


def sanitize_date_param(raw: str | None) -> str | None:
    """Validate and normalize a date/year parameter for `/api/1/search`."""
    if raw is None:
        return None
    cleaned = str(raw).strip()
    if not cleaned:
        return None
    if DATE_PARAM_RE.match(cleaned):
        return cleaned
    return None


class SearchService:
    """Service layer for querying the OpenAtlas `/api/1/search` endpoint."""

    def __init__(self, app: Any) -> None:
        self.api_url = app.config['API_URL']
        base = self.api_url.rstrip('/')
        if not base.endswith('/1'):
            base += '/1'
        self.api_v1_url = base
        self.search_url = f'{base}/search'
        proxy = app.config.get('API_PROXY')
        self.proxies = {'http': proxy, 'https': proxy}
        self.app_logger = app.logger

    @staticmethod
    def _normalize_item(
            item: dict[str, Any],
            case_study_id: int | None = None) -> dict[str, Any]:
        """Normalize a v1 search result item for frontend consumption."""
        normalized = dict(item)
        if 'id' in normalized and normalized['id'] is not None:
            raw_id = str(normalized['id'])
            normalized['id'] = (
                raw_id.rstrip('/').split('/')[-1]
                if '/' in raw_id else raw_id)
        sys_cls = (
            normalized.get('systemClass')
            or normalized.get('system_class')
            or '')
        normalized['systemClass'] = sys_cls
        normalized['system_class'] = sys_cls
        normalized['timespanDisplay'] = format_search_timespan(
            normalized.get('timespan'))
        if case_study_id is not None and 'caseStudyId' not in normalized:
            normalized['caseStudyId'] = case_study_id
        return normalized

    @staticmethod
    def _rank_key(query_lower: str, item: dict[str, Any]) -> tuple[int, str]:
        """Rank exact, prefix, and substring name matches before phonetic."""
        name_lower = str(item.get('name') or '').lower()
        if not query_lower:
            return 0, name_lower
        if name_lower == query_lower:
            return 0, name_lower
        if name_lower.startswith(query_lower):
            return 1, name_lower
        if query_lower in name_lower:
            return 2, name_lower
        return 3, name_lower

    def _fetch_page(
            self,
            params: dict[str, Any],
            headers: dict[str, str] | None = None,
            case_study_id: int | None = None) -> dict[str, Any]:
        """Execute a single GET request against `/api/1/search`."""
        req_headers = (
            headers if headers is not None
            else getattr(g, 'api_headers', {}))
        try:
            response = requests.get(
                self.search_url,
                params=params,
                headers=req_headers,
                proxies=self.proxies,
                timeout=10)
            response.raise_for_status()
            payload = response.json()
            if not isinstance(payload, dict):
                return {'items': [], 'total_items': 0}
            raw_items = payload.get('data')
            if not isinstance(raw_items, list):
                raw_items = payload.get('results', [])
            if not isinstance(raw_items, list):
                raw_items = []
            items = [
                self._normalize_item(item, case_study_id=case_study_id)
                for item in raw_items
                if isinstance(item, dict)]
            total = payload.get('totalItems')
            total_items = (
                int(total) if isinstance(total, int) else len(items))
            return {'items': items, 'total_items': total_items}
        except requests.exceptions.RequestException as exc:
            self.app_logger.error(
                f'API call error to {self.search_url}: {exc}')
            return {'items': [], 'total_items': 0}
        except json.JSONDecodeError as exc:
            self.app_logger.error(
                f'JSON decode error from {self.search_url}: {exc}')
            return {'items': [], 'total_items': 0}
        except Exception as exc:
            self.app_logger.error(
                f'Unexpected error for {self.search_url}: {exc}')
            return {'items': [], 'total_items': 0}

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    # pylint: disable=too-many-locals
    def execute_search(
            self,
            query: str = '',
            entity_classes: list[str] | None = None,
            case_study_ids: list[int] | None = None,
            start_date: str | None = None,
            end_date: str | None = None,
            sort_by: str = 'name',
            sort_order: str = 'asc',
            limit: int = 50,
            page: int = 1) -> dict[str, Any]:
        """Query `/api/1/search` with full filter, timespan, and sort options.

        Handles single or multiple case studies and optional entity classes
        concurrently, deduplicating entities by ID.
        """
        clean_query = (query or '').strip()
        valid_classes = [
            sc for sc in (entity_classes or [])
            if sc and sc != 'all' and sc in OPENATLAS_SEARCH_CLASSES]
        class_targets: list[str | None] = (
            valid_classes if valid_classes else [None])

        if case_study_ids is None:
            cs_ids = [
                int(cs) for cs in getattr(g, 'case_study_ids', []) if cs]
        else:
            cs_ids = [int(cs) for cs in case_study_ids if cs]
        cs_targets: list[int | None] = cs_ids if cs_ids else [None]

        clean_start = sanitize_date_param(start_date)
        clean_end = sanitize_date_param(end_date)
        clean_sort_by = sort_by if sort_by in VALID_SORT_BY else 'name'
        clean_sort = sort_order if sort_order in VALID_SORT_ORDER else 'asc'
        clean_limit = max(1, min(100, int(limit or 50)))
        clean_page = max(1, int(page or 1))

        headers = dict(getattr(g, 'api_headers', {}))
        call_specs: list[tuple[dict[str, Any], int | None]] = []
        for cs_id in cs_targets:
            for entity_class in class_targets:
                params: dict[str, Any] = {
                    'limit': clean_limit,
                    'page': clean_page,
                    'sortBy': clean_sort_by,
                    'sort': clean_sort}
                if clean_query:
                    params['search'] = clean_query
                if entity_class:
                    params['entityClass'] = entity_class
                if cs_id is not None:
                    params['caseStudy'] = cs_id
                if clean_start:
                    params['startDate'] = clean_start
                if clean_end:
                    params['endDate'] = clean_end
                call_specs.append((params, cs_id))

        responses: list[dict[str, Any]] = []
        if len(call_specs) == 1:
            params, cs_id = call_specs[0]
            responses.append(self._fetch_page(params, headers, cs_id))
        else:
            with ThreadPoolExecutor(
                    max_workers=min(8, len(call_specs))) as executor:
                futures = [
                    executor.submit(
                        self._fetch_page,
                        params,
                        headers,
                        cs_id)
                    for params, cs_id in call_specs]
                for future in futures:
                    responses.append(future.result())

        seen_ids: set[str] = set()
        merged_items: list[dict[str, Any]] = []
        total_items = 0
        for res in responses:
            total_items += int(res.get('total_items', 0))
            for item in res.get('items', []):
                item_id = str(item.get('id') or '')
                if item_id and item_id in seen_ids:
                    continue
                if item_id:
                    seen_ids.add(item_id)
                merged_items.append(item)

        if len(call_specs) > 1 and clean_query and clean_sort_by == 'name':
            query_lower = clean_query.lower()
            merged_items.sort(
                key=lambda item: self._rank_key(query_lower, item))

        return {
            'items': merged_items[:clean_limit],
            'total_items': max(total_items, len(merged_items)),
            'page': clean_page,
            'limit': clean_limit,
            'has_more': total_items > clean_page * clean_limit}

    def perform_live_search(
            self,
            query: str,
            system_classes: list[str] | None = None,
            case_study_ids: list[int] | None = None) -> list[dict[str, Any]]:
        """Perform a live autocomplete search against `/api/1/search`."""
        clean_query = (query or '').strip()
        if len(clean_query) < 3:
            return []
        result = self.execute_search(
            query=clean_query,
            entity_classes=system_classes,
            case_study_ids=case_study_ids,
            limit=20,
            page=1)
        return result['items']
