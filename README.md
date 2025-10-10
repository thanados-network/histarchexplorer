# Histarchexplorer

Histarchexplorer is a presentation application built for [OpenAtlas](https://openatlas.eu) — an open-source system for managing historical, archaeological, and cultural heritage data. 

The goal of Histarchexplorer is to **transform structured OpenAtlas datasets into rich, interactive visualizations**. It provides different ways of exploring research data such as:

- 🗺️ **Map Layers** – visualize sites, finds, and spatial relations.
- ⏳ **Event Timelines** – trace historical developments over time.
- 👥 **Person Networks** – uncover connections between historical actors.
- 🏺 **Archaeological Subunits & Finds** – browse catalogues of excavations and artefacts.

Designed for researchers, archaeologists, and historians, Histarchexplorer acts as a **bridge between OpenAtlas and the public presentation of knowledge**.

---

## 🚀 Features
- Integration with existing **OpenAtlas PostgreSQL + PostGIS** databases
- Flask-based backend for serving visualizations
- SCSS-based frontend styling with automatic compilation
- Flexible modules for different presentation forms (maps, networks, catalogues)

---

## ⚙️ Requirements
Histarchexplorer is developed and tested on **Debian 12** with the following stack:

- **Python**: 3.x
- **Flask**: 2.2.2
- **PostgreSQL**: 15
- **PostGIS**: 3
- **Apache**: 2.4 with WSGI
- **OpenAtlas** (required): running on the same database instance

---

## 🔧 Installation

### 1. System dependencies
Install Apache, gettext, npm:
```bash
sudo apt install apache2 libapache2-mod-wsgi-py3 gettext npm
```

Install PostgreSQL 15 with PostGIS 3:
```bash
sudo apt install postgresql postgresql-15-postgis-3 postgresql-15-postgis-3-scripts
```

### 2. Python dependencies
```bash
sudo apt install python3-bcrypt python3-flask python3-flask-babel \
    python3-flask-login python3-mypy python3-numpy python3-psycopg2 \
    python3-werkzeug python3-wtforms python3-flask-caching python3-requests
```

#### Development dependencies (optional)
```bash
sudo apt install python3-pytest python3-pytest-cov python3-pytest-flask
```

### 3. Clone the repository
Clone Histarchexplorer into `/var/www/`:
```bash
cd /var/www/
git clone https://github.com/thanados-network/histarchexplorer.git
```

### 4. Frontend setup (SCSS → CSS)
```bash
cd histarchexplorer/histarchexplorer/static
sass --watch scss/main.scss:css/main.css
```

### 5. Database setup
Histarchexplorer requires an existing **OpenAtlas PostgreSQL database**. To install the additional structures for presentation:

```bash
cd install
cat 1_structure.sql 2_data_model.sql | psql -d <DATABASE_NAME> -f -
```

Alternatively, run the installation script (requires correct credentials in `instance/production.py`):
```bash
export PYTHONPATH=".:$PYTHONPATH"
python3 install/install_script.py
```

### 6. Configure production settings
Copy the example production configuration:
```bash
cp instance/example_production.py instance/production.py
```

Edit `instance/production.py` to match your OpenAtlas database credentials:
```python
DATABASE_NAME = ''
DATABASE_USER = ''
DATABASE_PASS = ''
```

---

## 📂 Project Structure
```
Histarchexplorer/
├── config/              # Configuration file 
├── install/             # Database installation scripts
├── instance/            # Instance-specific configs (e.g., production.py)
└── histarchexplorer/    # Core Flask application
    ├── static/          # SCSS, CSS, JS, images
    ├── templates/       # HTML templates (Flask Jinja2)
└── tests/               # Unit and integration tests
```

---

## 📖 References
- [OpenAtlas Documentation](https://openatlas.eu)
- [OpenAtlas GitHub](https://github.com/craws/OpenAtlas)

---

## 🤝 Contributing
Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests to improve Histarchexplorer.

---

## 📜 License
This project is released under the [MIT License](LICENSE).



# Todo:
Include this in the README:

    npm install --production=false
    npm run build
