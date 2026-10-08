#!/usr/bin/env python3
"""Warm, refresh or age-refresh the entity cache in the background.

Modes: ``warm`` fetches only uncached entities, ``stale`` additionally
refetches entities older than ENTITY_CACHE_MAX_AGE_DAYS (suitable for a
weekly cron job) and ``refresh`` refetches everything. Started by the
admin dashboard with an inherited lock; run directly it takes the lock
itself and exits quietly if another warm-up is active.
"""

import argparse
import os

from histarchexplorer import app
from histarchexplorer.services.cache_jobs import timestamp
from histarchexplorer.services.entity_cache import (
    JOB_DEFAULTS, MODES, entity_job, run_entity_warmup)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', choices=MODES, default='warm')
    parser.add_argument('--case-studies', nargs='+', type=int, default=[])
    parser.add_argument('--lock-fd', type=int)
    args = parser.parse_args()
    with app.app_context():
        job = entity_job()
        fd = args.lock_fd
        if fd is None:
            fd = job.lock()
            if fd is None:
                return 0
            job.write(**dict(
                JOB_DEFAULTS, state='queued', mode=args.mode,
                started_at=timestamp()))
        try:
            state = run_entity_warmup(job, args.mode, args.case_studies)
        except BaseException:
            job.write(state='failed', finished_at=timestamp())
            raise
        finally:
            os.close(fd)
    return int(state == 'failed')


if __name__ == '__main__':
    raise SystemExit(main())
