"""Shared building blocks for detached cache jobs.

A job owns an exclusive host lock (``flock``) that its worker process
inherits for its whole lifetime, plus a small JSON status file. A status
that claims to be active while nobody holds the lock is reported as
``interrupted``, so crashed workers never look alive.
"""

import fcntl
import json
import os
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Optional

import requests
from flask import current_app, g

ACTIVE_STATES = ('queued', 'running')
MAX_ATTEMPTS = 3
ROOT = Path(__file__).resolve().parents[2]


def timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


class JobTracker:
    """Lock and persistent status for one named background job."""

    def __init__(self, name: str, defaults: dict[str, Any]) -> None:
        self.name = name
        self.defaults = defaults
        self.directory = Path(current_app.config.get(
            'CACHE_JOBS_DIR',
            Path(current_app.instance_path) / 'cache-jobs'))
        self.directory.mkdir(parents=True, exist_ok=True)

    @property
    def _status_path(self) -> Path:
        return self.directory / f'{self.name}.json'

    def lock(self) -> Optional[int]:
        """Return a file descriptor holding the job lock, or None if busy."""
        fd = os.open(
            self.directory / f'{self.name}.lock',
            os.O_CREAT | os.O_RDWR,
            0o600)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            os.close(fd)
            return None
        return fd

    def read(self) -> dict[str, Any]:
        try:
            stored = json.loads(self._status_path.read_text())
        except (OSError, ValueError):
            stored = {}
        return {key: stored.get(key, value)
                for key, value in self.defaults.items()}

    def write(self, **fields: Any) -> dict[str, Any]:
        """Merge fields into the status with an atomic file replacement."""
        status = self.read()
        status.update(fields, updated_at=timestamp())
        temporary = self._status_path.with_suffix(f'.{uuid.uuid4().hex}.tmp')
        try:
            temporary.write_text(json.dumps(status))
            os.replace(temporary, self._status_path)
        finally:
            temporary.unlink(missing_ok=True)
        return status

    def status(self) -> dict[str, Any]:
        """Return the status, flagging active jobs whose worker died."""
        status = self.read()
        if status['state'] in ACTIVE_STATES:
            fd = self.lock()
            if fd is not None:
                try:
                    status = self.write(
                        state='interrupted', finished_at=timestamp())
                finally:
                    os.close(fd)
        return status

    def start(
            self, script: str, arguments: list[str],
            initial: dict[str, Any]) -> bool:
        """Launch a detached worker. False means the job is already busy."""
        fd = self.lock()
        if fd is None:
            return False
        try:
            now = timestamp()
            self.write(**dict(
                self.defaults, **initial, state='queued', started_at=now,
                finished_at=''))
            subprocess.Popen(
                [sys.executable, str(ROOT / script), '--lock-fd', str(fd),
                 *arguments],
                cwd=str(ROOT), pass_fds=(fd,), start_new_session=True,
                stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL)
            return True
        except Exception:
            self.write(state='failed', finished_at=timestamp())
            raise
        finally:
            os.close(fd)


def retry_transient(operation: Callable[[], Any]) -> Any:
    """Retry connection errors, timeouts, 429 and 5xx with backoff."""
    for attempt in range(MAX_ATTEMPTS):
        try:
            return operation()
        except (requests.ConnectionError, requests.Timeout,
                requests.HTTPError) as error:
            status = (error.response.status_code
                      if error.response is not None else None)
            transient = (
                isinstance(error, (requests.ConnectionError, requests.Timeout))
                or status == 429
                or (status is not None and 500 <= status < 600))
            if not transient or attempt == MAX_ATTEMPTS - 1:
                raise
            time.sleep(2 ** attempt)


def set_api_headers() -> None:
    """Set the same authorization headers as the request hook does."""
    g.api_headers = {}
    if current_app.config.get('API_TOKEN'):
        g.api_headers['Authorization'] = (
            f"Bearer {current_app.config['API_TOKEN']}")
