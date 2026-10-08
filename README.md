# Histarchexplorer

[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.1+-green.svg)](https://flask.palletsprojects.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Histarchexplorer is a modern presentation application built for
[OpenAtlas](https://openatlas.eu). It transforms structured historical,
archaeological, and cultural heritage data into rich visualizations
using Vanilla JS, Bootstrap 5, and MapLibre.

- 🗺️ **Map Layers** – interactive visualization of sites and findings.
- ⏳ **Event Timelines** – trace historical developments over time.
- 👥 **Person Networks** – explore connections between historical actors.
- 🏺 **Archaeological Catalogues** – browse finds and excavation subunits.

---

## ⚙️ Requirements

Histarchexplorer is developed for **Debian 13**.

- **Stack**: Flask (Python 3.13+), PostgreSQL (17+) + PostGIS, Redis
- **Tooling**: `uv` (exclusively supported), `Node.js` (for frontend)
- **Deployment**: Apache2 + `mod_wsgi`

---

## 🔧 Installation

We exclusively use **`uv`** for Python dependency management.

### 1. System Dependencies

```bash
sudo apt update && sudo apt install -y \
    apache2 libapache2-mod-wsgi-py3 \
    postgresql redis-server libpq-dev \
    gettext npm curl
```

### 2. Setup `uv` & Project

```bash
# Install uv if not already present
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and install dependencies
git clone https://github.com/thanados-network/histarchexplorer.git
cd histarchexplorer
uv sync --group dev
```

### 3. Database Initialization

The project uses a dedicated reset script for database setup.

```bash
# Ensure the openatlas user exists
sudo -u postgres createuser openatlas

# Initialize database (creates tng_relic db and tng schema)
sudo -u postgres psql -f install/reset.sql
```

### 3b. Database Upgrades

The database schema and data updates are managed incrementally using semantic versioned SQL files located under
`install/upgrade/` (e.g., `install/upgrade/0.4.0.sql`).

To apply pending migrations, execute:
```bash
uv run python install/upgrade.py
```

This utility will:
1. Automatically create the `tng.schema_migrations` tracking table if it does not exist.
2. Scan the `install/upgrade/` directory for SQL files matching `[0-9]*.[0-9]*.[0-9]*.sql`.
3. Filter out migrations that have already been applied.
4. Execute pending migrations sequentially in semantic version order inside isolated transaction blocks.

#### Writing New Upgrades
When introducing schema or data changes:
1. Create a new SQL script in `install/upgrade/` named after the target version (e.g., `install/upgrade/0.5.0.sql`).
2. Do not include transaction control statements (`BEGIN`, `COMMIT`, `ROLLBACK`) since the upgrade runner automatically
   runs each file inside its own transaction block.

### 4. Configuration

```bash
cp instance/example_production.py instance/production.py
# Edit instance/production.py with your database credentials
```

### 5. Frontend & Translations

```bash
# Compile message catalogs
uv run ./histarchexplorer/translate.sh

# Build frontend assets
cd histarchexplorer/static
npm install && npm run build
cd ../..
```

### 6. Apache Deployment

```bash
sudo cp install/example_apache_uv.conf \
    /etc/apache2/sites-available/histarchexplorer.conf
sudo a2ensite histarchexplorer && sudo systemctl reload apache2
```

---

## 🧪 Development & Testing

### Running Tests
Use `pytest` via `uv` to ensure the correct environment. By default, slow tests are excluded:
```bash
uv run pytest
```

To run all tests (including slow ones):
```bash
uv run pytest -m ""
```

To run in parallel (faster, but may have database conflicts):
```bash
./tests/run_tests.sh parallel
```

For batch execution (file-by-file) to avoid timeouts in restricted environments:
```bash
./tests/run_tests.sh batch
```

### Coverage Report
```bash
uv run pytest --cov=histarchexplorer --cov-report=term-missing
```

### Frontend Watch Mode
For real-time SCSS compilation during development:
```bash
cd histarchexplorer/static && npm run dev
```

---

## 📂 Project Structure

- `histarchexplorer/` – Core application, templates, and static assets.
- `install/` – SQL initialization and deployment configuration examples.
- `instance/` – Local instance configuration (ignored by version control).
- `tests/` – Comprehensive test suite.

### Vocabulary viewer (0.6.0)

The default `/vocabulary` page embeds the unchanged
`openatlas-vocabulary-viewer` npm component. The menu-management switch
controls its navbar visibility, not access to the page or API. Administrators
and managers configure viewer-only include/exclude type IDs under
Content → Vocabulary. Content menu management offers Default and Individual
page types, just like other content pages.
The Viewer title field sets the widget header through its documented
`header-title` attribute, independently of the navbar label and page heading.
An empty title uses the widget's localized default. The title is plain text,
shared across languages; individual templates may use `settings.vocabulary_title`.

The component is installed directly from GitHub. Although `package.json`
does not name a release, `package-lock.json` pins a specific commit:
`npm install` normally reuses it and `npm ci` installs that exact revision.
To pull a newer GitHub revision, run `npm update openatlas-vocabulary-viewer`
in `histarchexplorer/static`, test the update and commit the updated lockfile.
Release tags are optional, but useful for managing stable upstream releases.

The widget uses its standard green palette and borders in a centered,
responsive Bootstrap container; dark mode adjusts surfaces and text for
contrast without changing the widget package.
Empty lists show everything; include retains selected subtrees and ancestors,
while exclude hides selected subtrees. Only one list may be nonempty.
Entity visibility settings remain independent. Invalid stored filters fall
back to the unfiltered vocabulary and are logged.

Upgrade `install/upgrade/0.6.0.sql` adds the JSONB defaults
`vocabulary_include_ids = []`, `vocabulary_exclude_ids = []`,
`vocabulary_title = ""`, and a visible
`menu_management.vocabulary` entry without replacing existing settings.
The standard upgrade runner handles transactions; no manual data changes
are required. Individual renders `uploads/templates/vocabulary.html` using
the existing custom-template mechanism, falling back to the default widget
when that file is absent. Existing installations keep the default page type;
selecting Individual uses the existing menu JSONB setting without a schema
change or additional migration.

The local `/api/vocabulary/tree` and `/api/vocabulary/<id>` endpoints proxy
OpenAtlas `/api/1/vocabulary/tree` and `/api/1/vocabulary/<id>`. They use the
configured API URL, server-side authentication, proxy and shared cache.
An API URL already ending in `/api/1/` is supported. The global access
restriction also applies to the viewer and its JSON endpoints. Filters are
presentation controls, **not** API access restrictions.

**Cache operation:** Refresh system cache starts `warm_vocabulary_cache.py`
in the background with the application's Python interpreter. This invalidates
both vocabulary memoize namespaces, reloads the full tree, and fetches every
unique type detail in all six categories with at most two concurrent requests.
Viewer filters do not reduce this preload. Transient failures are retried
with bounded backoff; permanent detail failures are counted without stopping
the remaining IDs. A failed tree fetch fails the job rather than reporting
completion. API credentials remain in server configuration, not process args.

The admin cache section shows the latest job state, detail counts and UTC
timestamps when loaded. A “started” notification is not a completion notice.
Large vocabularies may take hours and consume substantial cache memory;
the usual cache backend and data TTL still apply. Failed/missing details
remain available for an on-demand retry through the proxy. The existing
entity warmup process is unchanged. Build frontend assets using
`cd histarchexplorer/static && npm run build` after deployment.

Refresh coordination uses a lifetime host lock and a renewable owner lease,
so repeated refreshes cannot overlap and terminated jobs are reported as
interrupted. `VOCABULARY_REFRESH_DIR` defaults to
`instance/vocabulary-refresh` and must be writable by both web and worker
users. FileSystemCache installations keep coordination there. Redis
installations additionally use `VOCABULARY_REFRESH_REDIS_DB` (default:
application cache DB + 1), which **must be dedicated** and differ from the
cache DB. Redis credentials require `SELECT` and `EVAL` permissions for that
database. Global cache clear removes vocabulary data but deliberately leaves
coordination intact; a running preload can repopulate cleared data. Do not
clear the coordination database while a worker is running. No queue service
is required. For an explicit full preload from the configured environment,
run `uv run python warm_vocabulary_cache.py` from the project root.

### Entity cache and dashboard

Admin → Cache options is a dashboard: backend statistics (entries, size,
hit rate, lifetime; refreshed every two minutes), the age distribution of
cached entities and live progress of the entity and vocabulary jobs
(`/admin/cache-status` returns the same data as JSON).

Each API fetch of an entity stores a timestamp. An entity older than
`ENTITY_CACHE_MAX_AGE_DAYS` (default 7) is refetched when it is opened. Note
that `CACHE_DEFAULT_TIMEOUT` (default about 4 days) still expires entries
earlier; raise it for a longer lifetime. `warm_entity_cache.py` runs detached,
holds a lock (no parallel runs), uses two workers, retries transient API
errors and keeps its status. Modes: `warm` (only uncached entities), `stale`
(additionally entities older than the maximum age) and `refresh` (everything).
The pause (`ENTITY_WARMUP_DELAY`, default 1 s) applies only after real API
fetches, so already cached entities are skipped quickly. Entities cached
before the age tracking existed are adopted by the next run without refetching.
Set `ENTITY_WARMUP_BASE_URL` to the public site URL (default
`http://127.0.0.1:5000`), because cached models contain absolute links.
A weekly cron job keeps the cache fresh, for example:
`uv run python warm_entity_cache.py --mode stale`.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues, feature
requests, or pull requests to improve Histarchexplorer.

---

## 📜 License

This project is released under the [MIT License](LICENSE).
