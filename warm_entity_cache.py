#!/usr/bin/env python3
import argparse
import time
from typing import Any, Optional

import requests
import concurrent.futures

from config.default import API_URL

# Configuration
API_BASE = "http://127.0.0.1:5000"
MAX_WORKERS = 2


def get_by_system_class(
        case_study_ids: Optional[list[int]] = None) -> list[dict[str, Any]]:
    req = requests.get(
        f"{API_URL}system_class/all",
        params={
            'type_id': case_study_ids or [],
            'limit': 0,
            'show': ["none"],
            'format': "lpx"},
        timeout=60).json()

    return req['results']


def refresh_entity_cache(entity_id: int):
    """Clear and rebuild cache for one entity via admin endpoint."""
    time.sleep(1)
    url = f"{API_BASE}/refresh-cache/{entity_id}"
    try:
        requests.post(url, timeout=60)
    except Exception as e:
        print(f"Error refreshing {entity_id}: {e}")


def warm_entity_cache(entity_id: int):
    """Just trigger the cached endpoint."""
    time.sleep(1)
    url = f"{API_BASE}/presentation-view/{entity_id}"
    try:
        requests.get(url, timeout=60)
    except Exception as e:
        print(f"Error warming {entity_id}: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Warm or refresh entity cache.")
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Clear and rebuild cache before warming.")
    parser.add_argument(
        "--case-studies",
        nargs="+",
        type=int,
        help="List of case study IDs to fetch entities from (e.g. "
             "--case-studies 1 2 3)")
    args = parser.parse_args()
    if args.case_studies:
        entities = get_by_system_class(args.case_studies)
    else:
        entities = get_by_system_class()

    ids = [int(e["features"][0]["@id"].rsplit("/", 1)[-1]) for e in entities]

    func = refresh_entity_cache if args.refresh else warm_entity_cache

    with concurrent.futures.ThreadPoolExecutor(
            max_workers=MAX_WORKERS) as executor:
        executor.map(func, ids)


if __name__ == "__main__":
    main()
