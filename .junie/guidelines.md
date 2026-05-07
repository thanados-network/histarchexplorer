### Projekt-Details
- **Name**: Histarchexplorer (tng)
- **Stack**: Flask (Python 3.13+), PostgreSQL (17+) mit PostGIS, Redis (Caching), libsass (SCSS)
- **Frontend**: Vanilla JS (ES6+), Bootstrap 5 (CSS), Leaflet/MapLibre (Karten)

### Build-Schritte
1. **Abhängigkeiten**:
   - `uv sync --group dev` (Empfohlen) oder `apt` (System-Pakete)
   - `npm install` (für Frontend-Assets, falls vorhanden)
2. **SCSS Kompilierung**:
   - Erfolgt i.d.R. zur Laufzeit via `libsass` oder dediziertes Skript (falls vorhanden).
3. **Datenbank**:
   - Initialisierung via `install/reset.sql`.
4. **Übersetzungen**:
   - `./histarchexplorer/translate.sh` ausführen.

### Test-Setup
- **Framework**: `pytest` mit `pytest-flask`
- **Ausführung**: `pytest` im Root-Verzeichnis.
- **Konfiguration**: `tests/conftest.py` enthält die Flask-App-Fixture.
- **Coverage**: `pytest --cov=histarchexplorer`

### Coding-Standards
- **Python**: PEP 8 konform, **strikt max. 79 Zeichen** Zeilenlänge.
- **HTML/JS/SCSS**: **strikt max. 120 Zeichen** Zeilenlänge.
- **Klammern**: Schließende `]` oder `)` immer in derselben Zeile wie das letzte Element.
- **Variablen**: CamelCase in JS, kebab-case in SCSS. Keine Docstrings.
- **Struktur**: 1-2 Leerzeilen zur logischen Trennung.
