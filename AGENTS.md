# Histarchexplorer (tng) – Agent Guidelines

## Stack & Commands
- **Backend**: Flask (Python 3.13+), PostgreSQL 17+ (PostGIS), Redis, libsass
- **Frontend**: Vanilla JS (ES6+), Bootstrap 5, Leaflet/MapLibre
- **Deps**: `uv sync --group dev` or system `apt` packages
- **DB Init**: `install/reset.sql`
- **Translations**: `./histarchexplorer/translate.sh`
- **Tests**: `pytest` (Coverage: `pytest --cov=histarchexplorer`, skip slow: `pytest -m "not slow"`)

## Testing & Database Rules (Strict)
- **External APIs**: Calls to external services (e.g., `thanados.openatlas.eu`) MUST be mocked (see `tests/conftest.py`).
- **DB Upgrades**: Every schema/data change requires a migration script in `install/upgrade/` (e.g., `0.5.0.sql`).
- **No Transaction Keywords**: Never write `BEGIN`, `COMMIT`, or `ROLLBACK` inside `install/upgrade/*.sql` files. The upgrade runner wraps files in transactions automatically.

## Non-Standard Code & Architecture Rules
- **Line Length**: Python max **79 chars**; HTML/JS/SCSS max **120 chars**.
- **Closing Brackets (Quirk)**: Place closing `]` or `)` on the **same line** as the last element (do NOT use Black-style trailing closing brackets on a new line):
  ```python
  def apply_migration(
      cursor: Any,
      filepath: Path,
      version: str) -> None:
Jinja2 vs. JS: Inline <script> in Jinja2 is ONLY allowed for view initialization or config bootstrapping. Pass simple values via HTML5 data-* attributes; put logic into external .js files.

