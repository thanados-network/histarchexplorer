#!/usr/bin/env python3
import requests
import concurrent.futures
from pathlib import Path

API_BASE = "http://127.0.0.1:5000/presentation-view/"
INPUT_FILE = Path("cache_ids.txt")  # one ID per line
MAX_WORKERS = 8  # number of concurrent requests


def warm_cache_for_id(entity_id: int):
    url = f"{API_BASE}{entity_id}"
    try:
        r = requests.get(url, timeout=60)
        #  if r.ok:
        #      print(f"✅ Cached {entity_id}")
        #  else:
        #      print(f"⚠️ Failed {entity_id}: {r.status_code}")
    except Exception as e:
        print(f"❌ Error {entity_id}: {e}")


def main():
    ids = [
        int(line.strip())
        for line in INPUT_FILE.read_text().splitlines() if line.strip()]
    #print(f"🌡️ Warming cache for {len(ids)} entities")

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        executor.map(warm_cache_for_id, ids)

    print("🔥 Cache warmup completed")


if __name__ == "__main__":
    main()
