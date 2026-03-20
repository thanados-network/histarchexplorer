# Histarchexplorer

Histarchexplorer is a presentation application built for
[OpenAtlas](https://openatlas.eu) — an open-source system for managing
historical, archaeological, and cultural heritage data.

The goal of Histarchexplorer is to **transform structured OpenAtlas datasets
into rich, interactive visualizations**. It provides different ways of
exploring research data such as:

- 🗺️ **Map Layers** – visualize sites, finds, and spatial relations.
- ⏳ **Event Timelines** – trace historical developments over time.
- 👥 **Person Networks** – uncover connections between historical actors.
- 🏺 **Archaeological Subunits & Finds** – browse catalogues of excavations and
  artefacts.

Designed for researchers, archaeologists, and historians, Histarchexplorer acts
as a **bridge between OpenAtlas and the public presentation of knowledge**.

---

## ⚙️ Requirements

Histarchexplorer is developed and tested on **Debian 13** with the following
stack:

- **OS**: Debian 13
- **Python**: 3.13+
- **PostgreSQL**: 17+ with PostGIS 3+
- **Redis**: Recommended for caching
- **Apache2** with `mod_wsgi`
- **OpenAtlas**: A running instance on the same database server.

---

## 🔧 Installation

This guide provides two paths for Python dependency management:
- **`uv` (Recommended)**: Uses a virtual environment for isolated, project-specific packages.
- **`apt`**: Uses system-wide packages managed by Debian.

### 1. Base System Setup

First, install common dependencies for both methods:

```bash
sudo apt update
sudo apt install \
    apache2 libapache2-mod-wsgi-py3 \
    postgresql redis-server libpq-dev \
    gettext npm
```

### 2. Clone the Repository

```bash
git clone https://github.com/thanados-network/histarchexplorer.git
cd histarchexplorer
```

---

### 🚀 Path A: `uv` (Recommended)

This method isolates project dependencies in a `.venv` directory.

#### 2.1. Install `uv`

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
Source your profile (e.g., `source ~/.bashrc`) or restart your shell.

#### 2.2. Install Python Dependencies

This command creates the `.venv` and installs packages from `uv.lock`.

```bash
uv sync
```

For development tools (like `pytest`), use the `dev` group:
```bash
uv sync --group dev
```

---

### 📦 Path B: `apt` (System Packages)

This method uses Debian's package manager for all Python dependencies.

#### 2.1. Install Python Dependencies

```bash
sudo apt install \
    python3-bcrypt python3-flask python3-flask-babel \
    python3-flask-login python3-mypy python3-numpy \
    python3-psycopg2 python3-werkzeug python3-wtforms \
    python3-flask-caching python3-requests python3-redis \
    python3-bleach python3-libsass python3-pydantic
```

For development, install `pytest`:
```bash
sudo apt install python3-pytest python3-pytest-cov python3-pytest-flask
```

---

### 3. Final Setup Steps (Both Paths)

#### 3.1. Database Setup

Create a new database for Histarchexplorer:

```bash
sudo -u postgres createdb <DATABASE_NAME> -O openatlas
cat install/1_structure.sql install/2_data_model.sql | sudo -u postgres psql -d <DATABASE_NAME>
```

#### 3.2. Configuration

Copy and edit the production configuration:

```bash
cp instance/example_production.py instance/production.py
# Edit instance/production.py with your database credentials
```

#### 3.3. Frontend Setup (SCSS/JS)

Install Node.js dependencies and build the CSS files.

```bash
cd histarchexplorer/static
npm install
npm run build
cd ../.. # Return to project root
```

For frontend development, you can use `npm run dev` to automatically watch for
SCSS changes.

#### 3.4. Apache Configuration

Copy the appropriate example configuration and enable the site.

- **For `uv` installs**:
  ```bash
  sudo cp install/example_apache_uv.conf /etc/apache2/sites-available/histarchexplorer.conf
  ```
- **For `apt` installs**:
  ```bash
  sudo cp install/example_apache_apt.conf /etc/apache2/sites-available/histarchexplorer.conf
  ```

Then, enable the site and restart Apache:
```bash
sudo a2ensite histarchexplorer
sudo systemctl reload apache2
```

---

## 🧪 Running Tests

1.  **Create a Test Database**:
    ```bash
    sudo -u postgres createdb histarchexplorer_test -O openatlas
    ```

2.  **Configure Test Environment**:
    Copy `example_testing.py` to `instance/testing.py` and edit the database name.

3.  **Run Tests**:
    - **`uv` path**: Activate the environment first: `source .venv/bin/activate && pytest`
    - **`apt` path**: Simply run `pytest`

---

## 📂 Project Structure

```
Histarchexplorer/
├── install/             # Database and deployment scripts
├── instance/            # Instance-specific configs (production.py)
└── histarchexplorer/    # Core Flask application
    ├── static/          # SCSS, CSS, JS, images
    ├── templates/       # HTML templates (Jinja2)
└── tests/               # Unit and integration tests
```

---

## 📖 References

- [OpenAtlas Documentation](https://openatlas.eu)
- [OpenAtlas GitHub](https://github.com/craws/OpenAtlas)

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues, feature requests,
or pull requests to improve Histarchexplorer.

---

## 📜 License

This project is released under the [MIT License](LICENSE).
