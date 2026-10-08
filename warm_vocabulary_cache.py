#!/usr/bin/env python3
"""Background vocabulary cache worker using configured Flask API access."""

import argparse
import os
import uuid

from histarchexplorer import app
from histarchexplorer.services.vocabulary_cache import (
    _Coordinator, _empty_status, _timestamp, run_vocabulary_refresh)


def main() -> int:
    """Use an inherited job lock, or acquire one for a direct CLI refresh."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--job-token')
    parser.add_argument('--lock-fd', type=int)
    args = parser.parse_args()
    if (args.job_token is None) != (args.lock_fd is None):
        parser.error('--job-token and --lock-fd must be supplied together')
    with app.app_context():
        token = args.job_token
        fd = args.lock_fd
        if token is None:
            coordinator = _Coordinator(app)
            fd = coordinator.host_lock()
            if fd is None:
                return 0
            token = uuid.uuid4().hex
            now = _timestamp()
            status = dict(_empty_status(), state='queued', started_at=now,
                          updated_at=now)
            try:
                acquired = coordinator.acquire(token, status)
            except Exception:
                os.close(fd)
                raise
            if not acquired:
                os.close(fd)
                return 0
        result = run_vocabulary_refresh(token, fd)
    return int(result['state'] == 'failed')


if __name__ == '__main__':
    raise SystemExit(main())
