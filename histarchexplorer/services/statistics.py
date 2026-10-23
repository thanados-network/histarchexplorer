"""Wissenschaftliche Statistik- und Geodatendienste für die Startseite."""
from typing import Any

from flask import g

from histarchexplorer import cache


def _safe_case_study_tuple(
        case_study_ids: tuple[int, ...] | list[int] | None) -> tuple[int, ...]:
    """Sicherstellen, dass case_study_ids ein gültiges Tuple ist."""
    if not case_study_ids:
        return ()
    return tuple(int(cid) for cid in case_study_ids if isinstance(cid, int))


@cache.memoize(timeout=86400)
def get_landing_statistics(
        case_study_ids: tuple[int, ...]) -> dict[str, Any]:
    """Aggregierte Forschungsdaten für Diagramme und wissenschaftliche KPIs.

    Args:
        case_study_ids: Tuple von Fallstudien-IDs zur Filterung.

    Returns:
        Dictionary mit Chronologie, Fundplatztypen, Fundkategorien und KPIs.
    """
    default_stats: dict[str, Any] = {
        'chronology': [],
        'site_types': [],
        'artifact_types': [],
        'kpis': {
            'places': 0, 'features': 0, 'artifacts': 0,
            'human_remains': 0, 'references': 0, 'files': 0}}

    if not hasattr(g, 'openatlas_cursor') or g.openatlas_cursor is None:
        return default_stats
    if not case_study_ids:
        return default_stats

    cs_tuple = _safe_case_study_tuple(case_study_ids)
    if not cs_tuple:
        return default_stats

    try:
        # 1. Chronologische Verteilung (nach Jahrhunderten 300 - 1500 n. Chr.)
        chrono_sql = """
            SELECT
                (FLOOR(EXTRACT(YEAR FROM e.begin_from) / 100) * 100)::int
                    AS century,
                COUNT(*) AS count
            FROM model.entity e
            JOIN model.link l1 ON l1.domain_id = e.id
                AND l1.property_code = 'P2'
            WHERE l1.range_id IN %s
              AND e.begin_from IS NOT NULL
              AND EXTRACT(YEAR FROM e.begin_from) BETWEEN 300 AND 1500
            GROUP BY century
            ORDER BY century
        """
        g.openatlas_cursor.execute(chrono_sql, (cs_tuple,))
        chronology = [
            {'century': f"{row['century']} CE",
             'year': row['century'],
             'count': row['count']}
            for row in g.openatlas_cursor.fetchall()]

        # 2. Fundplatztypen (Top 6 signifikante Typen)
        st_sql = """
            SELECT c.name AS name, COUNT(*) AS count
            FROM model.entity a
            JOIN model.link l1 ON l1.domain_id = a.id
                AND l1.property_code = 'P2'
            JOIN model.link l2 ON l2.domain_id = a.id
                AND l2.property_code = 'P2'
            JOIN model.entity c ON c.id = l2.range_id
            WHERE l1.range_id IN %s
              AND a.openatlas_class_name = 'place'
              AND c.id NOT IN %s
              AND c.name NOT IN (
                  'RELIC', 'Replico', 'DeVill', 'THANADOS', 'Zbiva',
                  'Not present', 'Number of Graves')
            GROUP BY c.name
            ORDER BY count DESC
            LIMIT 6
        """
        g.openatlas_cursor.execute(st_sql, (cs_tuple, cs_tuple))
        site_types = [
            {'name': row['name'], 'count': row['count']}
            for row in g.openatlas_cursor.fetchall()]

        # 3. Fundkategorien / Material (Top 6 Typen)
        art_sql = """
            SELECT c.name AS name, COUNT(*) AS count
            FROM model.entity a
            JOIN model.link l1 ON l1.domain_id = a.id
                AND l1.property_code = 'P2'
            JOIN model.link l2 ON l2.domain_id = a.id
                AND l2.property_code = 'P2'
            JOIN model.entity c ON c.id = l2.range_id
            WHERE l1.range_id IN %s
              AND a.openatlas_class_name = 'artifact'
              AND c.id NOT IN %s
              AND c.name NOT IN (
                  'Length', 'Width', 'Count', 'Number', 'Height',
                  'Depth from', 'Depth to', 'Weight', 'THANADOS', 'Zbiva',
                  'RELIC', 'Replico')
            GROUP BY c.name
            ORDER BY count DESC
            LIMIT 6
        """
        g.openatlas_cursor.execute(art_sql, (cs_tuple, cs_tuple))
        artifact_types = [
            {'name': row['name'], 'count': row['count']}
            for row in g.openatlas_cursor.fetchall()]

        # 4. Klassen-Zählung für KPIs
        kpi_sql = """
            SELECT e.openatlas_class_name, COUNT(*) AS count
            FROM model.entity e
            JOIN model.link l1 ON l1.domain_id = e.id
                AND l1.property_code = 'P2'
            WHERE l1.range_id IN %s
              AND e.openatlas_class_name IN (
                  'place', 'feature', 'artifact', 'human_remains',
                  'bibliography', 'file')
            GROUP BY e.openatlas_class_name
        """
        g.openatlas_cursor.execute(kpi_sql, (cs_tuple,))
        kpi_counts = {
            row['openatlas_class_name']: row['count']
            for row in g.openatlas_cursor.fetchall()}

        return {
            'chronology': chronology,
            'site_types': site_types,
            'artifact_types': artifact_types,
            'kpis': {
                'places': kpi_counts.get('place', 0),
                'features': kpi_counts.get('feature', 0),
                'artifacts': kpi_counts.get('artifact', 0),
                'human_remains': kpi_counts.get('human_remains', 0),
                'references': kpi_counts.get('bibliography', 0),
                'files': kpi_counts.get('file', 0)}}
    except Exception:
        return default_stats


@cache.memoize(timeout=86400)
def get_landing_sites_geojson(
        case_study_ids: tuple[int, ...],
        limit: int = 5000) -> dict[str, Any]:
    """Erstellt ein leichtgewichtiges GeoJSON aller Fundorte für die Karte.

    Args:
        case_study_ids: Tuple von Fallstudien-IDs zur Filterung.
        limit: Maximale Anzahl von Fundorten.

    Returns:
        GeoJSON FeatureCollection Dictionary.
    """
    empty_fc: dict[str, Any] = {
        'type': 'FeatureCollection',
        'features': []}

    if not hasattr(g, 'openatlas_cursor') or g.openatlas_cursor is None:
        return empty_fc
    if not case_study_ids:
        return empty_fc

    cs_tuple = _safe_case_study_tuple(case_study_ids)
    if not cs_tuple:
        return empty_fc

    try:
        query = """
            SELECT
                e.id,
                e.name,
                ST_X(COALESCE(
                    g.geom_point, ST_Centroid(g.geom_polygon))) AS lng,
                ST_Y(COALESCE(
                    g.geom_point, ST_Centroid(g.geom_polygon))) AS lat,
                tng.getdates(
                    e.begin_from, e.begin_to, e.begin_comment) AS begin,
                tng.getdates(
                    e.end_to, e.end_from, e.end_comment) AS end
            FROM model.entity e
            JOIN model.link l1 ON l1.domain_id = e.id
                AND l1.property_code = 'P2'
            JOIN model.link lg ON lg.domain_id = e.id
                AND lg.property_code = 'P53'
            JOIN model.gis g ON g.entity_id = lg.range_id
            WHERE l1.range_id IN %s
              AND e.openatlas_class_name = 'place'
              AND (g.geom_point IS NOT NULL OR g.geom_polygon IS NOT NULL)
            LIMIT %s
        """
        g.openatlas_cursor.execute(query, (cs_tuple, limit))
        rows = g.openatlas_cursor.fetchall()

        features = []
        for r in rows:
            if r['lng'] is None or r['lat'] is None:
                continue
            date_label = ""
            if r['begin'] and r['end']:
                date_label = f"{r['begin']} – {r['end']}"
            elif r['begin']:
                date_label = f"ab {r['begin']}"

            features.append({
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [round(r['lng'], 6), round(r['lat'], 6)]},
                'properties': {
                    'id': r['id'],
                    'name': r['name'],
                    'dating': date_label}})

        return {
            'type': 'FeatureCollection',
            'features': features}
    except Exception:
        return empty_fc
