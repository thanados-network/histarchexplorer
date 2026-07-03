### Project Details
- **Name**: Histarchexplorer (tng)
- **Stack**: Flask (Python 3.13+), PostgreSQL (17+) with PostGIS, Redis (Caching), libsass (SCSS)
- **Frontend**: Vanilla JS (ES6+), Bootstrap 5 (CSS), Leaflet/MapLibre (Maps)

### Build Steps
1. **Dependencies**:
   - `uv sync --group dev` (Recommended) or `apt` (system packages)
   - `npm install` (for frontend assets, if present)
2. **SCSS Compilation**:
   - Usually occurs at runtime via `libsass` or dedicated script (if present).
3. **Database**:
   - Initialization via `install/reset.sql`.
4. **Translations**:
   - Execute `./histarchexplorer/translate.sh`.

### Test Setup
- **Framework**: `pytest` with `pytest-flask`
- **Execution**: `pytest` in the root directory.
- **Configuration**: `tests/conftest.py` contains the Flask app fixture.
- **Coverage**: `pytest --cov=histarchexplorer`
- **Optimization**:
  - External API calls (e.g. to `thanados.openatlas.eu`) MUST be mocked (see `tests/conftest.py`).
  - Slow tests should be marked with `@pytest.mark.slow` and can be excluded with `-m "not slow"`.

### Database Upgrades
- **Track changes**: Any change to the schema or data *must* be fully documented.
- **Workflow for updates**:
  - Check if a matching upgrade file exists in `install/upgrade/` (e.g., `0.4.0.sql`).
  - If not, create a new SQL file with the next version (e.g., `install/upgrade/0.5.0.sql`).
  - Never make undocumented database changes.
- **Transaction Safety**:
  - All upgrades are executed by the runner inside isolated database transaction blocks.
  - Do NOT write transaction control keywords (`BEGIN`, `COMMIT`, `ROLLBACK`) inside the SQL files
    themselves. This ensures that if a script fails midway, it is fully and safely rolled back, and
    can be retried cleanly.

### Coding Standards
- **Prinzipien**: Beachte immer KISS (Keep It Simple, Stupid) und DRY (Don't Repeat Yourself).
- **Python**: PEP 8 compliant, **strict max. 79 characters** line length.
- **HTML/JS/SCSS**: **strict max. 120 characters** line length.
- **Brackets/Parentheses**: Closing `]` or `)` always on the same line as the last element.
  - For function definitions:
    ```python
    # Not desired:
    def apply_migration(
        cursor: Any,
        filepath: Path,
        version: str
    ) -> None:

    # Desired:
    def apply_migration(
        cursor: Any,
        filepath: Path,
        version: str) -> None:
    ```
- **Variables**: camelCase in JS, kebab-case in SCSS.
- **Docstrings**: Required for important functions and unclear structures:
  - Flask views / API endpoints
  - Complex algorithms
  - Core data models / schemas
- **Structure**: 1-2 empty lines for logical separation.

#### JavaScript (Vanilla JS Specifics)
- **Scope & Variables**: Never use `var`. Use `const` by default; use `let` only if reassignment is explicitly required.
- **Modularity & State**: Avoid polluting the global scope. Enforce encapsulation using ES Modules (`import`/`export`) or immediately invoked function expressions (IIFE) where modules aren't viable.
- **DOM Manipulation & Performance**:
  - Cache DOM selectors (do not repeatedly query the DOM for the same element).
  - Use `DocumentFragment` when creating and appending multiple elements dynamically to prevent redundant reflows.
  - Prefer `element.textContent` over `element.innerHTML` unless rendering actual HTML, to avoid XSS vulnerabilities.
- **Asynchronous Operations**:
  - Always handle asynchronous actions using `async/await` syntax combined with structured `try/catch` blocks.
  - Provide meaningful error indicators or fallback states in the UI if a `fetch` or API call fails.
- **Clean Functions**: Functions must be single-purpose. Keep them compact, and if a function requires more than 3 arguments, pass them as a single configuration object instead.
