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
Use `pytest` via `uv` to ensure the correct environment:
```bash
uv run pytest
```

### Coverage Report
```bash
uv run pytest --cov=histarchexplorer
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

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues, feature
requests, or pull requests to improve Histarchexplorer.

---

## 📜 License

This project is released under the [MIT License](LICENSE).
