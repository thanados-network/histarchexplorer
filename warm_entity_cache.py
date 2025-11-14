#!/usr/bin/env python3
import argparse
import time

import requests
import concurrent.futures
from pathlib import Path

# Configuration
API_BASE = "http://127.0.0.1:5000"
INPUT_FILE = Path("cache_ids.txt")
MAX_WORKERS = 2


def refresh_entity_cache(entity_id: int):
    """Clear and rebuild cache for one entity via admin endpoint."""
    time.sleep(0.2)
    url = f"{API_BASE}/refresh-cache/{entity_id}"
    try:
        requests.post(url, timeout=60)
    except Exception as e:
        print(f"Error refreshing {entity_id}: {e}")


def warm_entity_cache(entity_id: int):
    """Just trigger the cached endpoint."""
    time.sleep(0.2)
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
    args = parser.parse_args()
    ids = [
        int(line.strip()) for line in
        INPUT_FILE.read_text().splitlines() if line.strip()]

    func = refresh_entity_cache if args.refresh else warm_entity_cache

    with concurrent.futures.ThreadPoolExecutor(
            max_workers=MAX_WORKERS) as executor:
        executor.map(func, ids)

if __name__ == "__main__":
    main()
