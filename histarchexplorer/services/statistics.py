"""Wissenschaftliche Statistik- und Geodatendienste für die Startseite."""
from typing import Any

from flask import g
from flask_babel import lazy_gettext as _l

from histarchexplorer import app, cache

CLASS_KPI_META: dict[str, dict[str, str]] = {
    'place': {
        'label': _l('Place'),
        'icon': 'bi-geo-alt',
        'image': 'place.png',
        'color_key': 'places',
        'tab': 'places'},
    'feature': {
        'label': _l('Feature'),
        'icon': 'bi-layers',
        'image': 'feature.png',
        'color_key': 'features',
        'tab': 'features'},
    'stratigraphic_unit': {
        'label': _l('Stratigraphic Unit'),
        'icon': 'bi-stack',
        'image': 'stratigraphic_unit.png',
        'color_key': 'stratigraphic_unit',
        'tab': 'features'},
    'artifact': {
        'label': _l('Artifact'),
        'icon': 'bi-gem',
        'image': 'artifact.png',
        'color_key': 'items',
        'tab': 'items'},
    'human_remains': {
        'label': _l('Human Remains'),
        'icon': 'bi-person-standing',
        'image': 'human remains.png',
        'color_key': 'remains',
        'tab': 'items'},
    'person': {
        'label': _l('Person'),
        'icon': 'bi-person',
        'image': 'person.png',
        'color_key': 'actors',
        'tab': 'actors'},
    'group': {
        'label': _l('Group'),
        'icon': 'bi-people',
        'image': 'group.png',
        'color_key': 'actors',
        'tab': 'actors'},
    'acquisition': {
        'label': _l('Acquisition'),
        'icon': 'bi-arrow-left-right',
        'image': 'event.png',
        'color_key': 'events',
        'tab': 'events'},
    'event': {
        'label': _l('Event'),
        'icon': 'bi-calendar-event',
        'image': 'event.png',
        'color_key': 'events',
        'tab': 'events'},
    'activity': {
        'label': _l('Activity'),
        'icon': 'bi-activity',
        'image': 'event.png',
        'color_key': 'events',
        'tab': 'events'},
    'creation': {
        'label': _l('Creation'),
        'icon': 'bi-hammer',
        'image': 'event.png',
        'color_key': 'events',
        'tab': 'events'},
    'move': {
        'label': _l('Move'),
        'icon': 'bi-signpost-split',
        'image': 'event.png',
        'color_key': 'events',
        'tab': 'events'},
    'production': {
        'label': _l('Production'),
        'icon': 'bi-tools',
        'image': 'event.png',
        'color_key': 'events',
        'tab': 'events'},
    'modification': {
        'label': _l('Modification'),
        'icon': 'bi-sliders',
        'image': 'event.png',
        'color_key': 'events',
        'tab': 'events'},
    'source': {
        'label': _l('Source'),
        'icon': 'bi-journal-text',
        'image': 'source.png',
        'color_key': 'sources',
        'tab': 'sources'},
    'bibliography': {
        'label': _l('Bibliography'),
        'icon': 'bi-book',
        'image': 'bibliography.svg',
        'color_key': 'sources',
        'tab': 'sources'},
    'external_reference': {
        'label': _l('External Reference'),
        'icon': 'bi-link-45deg',
        'image': 'source.png',
        'color_key': 'sources',
        'tab': 'sources'},
    'edition': {
        'label': _l('Edition'),
        'icon': 'bi-journal-bookmark',
        'image': 'source.png',
        'color_key': 'sources',
        'tab': 'sources'},
    'file': {
        'label': _l('File'),
        'icon': 'bi-image',
        'image': 'file.png',
        'color_key': 'files',
        'tab': 'files'},
    'type': {
        'label': _l('Type'),
        'icon': 'bi-tags',
        'image': 'item.png',
        'color_key': 'types',
        'tab': 'types'}}

VIEW_CLASS_META: dict[str, dict[str, str]] = {
    'places': {
        'tab_label': _l('Places'),
        'title': _l('Sites & Cemeteries'),
        'description': _l(
            'Archaeological sites, cemeteries, churches, and settlement '
            'structures with coordinates.'),
        'button_label': _l('Browse places'),
        'btn_class': 'btn-outline-success',
        'icon': 'bi-geo-alt',
        'image': 'place.png'},
    'features': {
        'tab_label': _l('Features'),
        'title': _l('Features & Structures'),
        'description': _l(
            'Grave constructions, burials, anthropological features, and '
            'stratigraphic units.'),
        'button_label': _l('Browse features'),
        'btn_class': 'btn-outline-secondary',
        'icon': 'bi-layers',
        'image': 'feature.png'},
    'items': {
        'tab_label': _l('Items'),
        'title': _l('Material Culture'),
        'description': _l(
            'Archaeological artifacts, jewelry, ceramics, weapons, dress '
            'accessories, and skeletal remains.'),
        'button_label': _l('Browse items'),
        'btn_class': 'btn-outline-warning text-dark',
        'icon': 'bi-gem',
        'image': 'item.png'},
    'actors': {
        'tab_label': _l('Actors'),
        'title': _l('Actors & Groups'),
        'description': _l(
            'Historical persons, individuals, institutions, and social '
            'groups.'),
        'button_label': _l('Browse actors'),
        'btn_class': 'btn-outline-danger',
        'icon': 'bi-people',
        'image': 'actor.png'},
    'events': {
        'tab_label': _l('Events'),
        'title': _l('Events & Activities'),
        'description': _l(
            'Historical events, archaeological activities, productions, '
            'movements, and acquisitions.'),
        'button_label': _l('Browse events'),
        'btn_class': 'btn-outline-info',
        'icon': 'bi-calendar-event',
        'image': 'event.png'},
    'sources': {
        'tab_label': _l('Sources'),
        'title': _l('Sources & Literature'),
        'description': _l(
            'Specialized bibliography, primary sources, and links to '
            'external authority files.'),
        'button_label': _l('View sources'),
        'btn_class': 'btn-outline-dark',
        'icon': 'bi-book',
        'image': 'source.png'},
    'files': {
        'tab_label': _l('Files'),
        'title': _l('Media & 3D'),
        'description': _l(
            'Digital media assets, photographs, drawings, and 3D models '
            'of entities.'),
        'button_label': _l('Browse media'),
        'btn_class': 'btn-outline-primary',
        'icon': 'bi-image',
        'image': 'file.png'},
    'types': {
        'tab_label': _l('Types'),
        'title': _l('Typology & Vocabulary'),
        'description': _l(
            'Controlled vocabularies, typological classifications, and '
            'hierarchical concepts.'),
        'button_label': _l('Browse types'),
        'btn_class': 'btn-outline-primary',
        'icon': 'bi-tags',
        'image': 'item.png'}}


def _safe_case_study_tuple(
        case_study_ids: tuple[int, ...] | list[int] | None) -> tuple[
            int, ...]:
    """Sicherstellen, dass case_study_ids ein gültiges Tuple ist."""
    if not case_study_ids:
        return ()
    return tuple(int(cid) for cid in case_study_ids if isinstance(cid, int))


@cache.memoize(timeout=86400)
def get_landing_statistics(
        case_study_ids: tuple[int, ...],
        cache_version: int = 2) -> dict[str, Any]:
    """Aggregierte Forschungsdaten für Diagramme und wissenschaftliche KPIs.

    Args:
        case_study_ids: Tuple von Fallstudien-IDs zur Filterung.
        cache_version: Versionsschlüssel zur Cache-Invalidierung.

    Returns:
        Dictionary mit Chronologie, Fundplatztypen, Fundkategorien und KPIs.
    """
    _ = cache_version
    default_stats: dict[str, Any] = {
        'chronology': [],
        'site_types': [],
        'artifact_types': [],
        'class_counts': {},
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

        # 2. Fundplatztypen (Top 6 Standard-Typen)
        st_sql = """
            WITH RECURSIVE standard_types AS (
                SELECT h.id AS id
                FROM web.hierarchy h
                WHERE h.category = 'standard'
                UNION ALL
                SELECT l.domain_id AS id
                FROM model.link l
                JOIN standard_types st ON l.range_id = st.id
                WHERE l.property_code = 'P127'
            )
            SELECT c.name AS name, COUNT(DISTINCT a.id) AS count
            FROM model.entity a
            JOIN model.link l1 ON l1.domain_id = a.id
                AND l1.property_code = 'P2'
            JOIN model.link l2 ON l2.domain_id = a.id
                AND l2.property_code = 'P2'
            JOIN standard_types st ON st.id = l2.range_id
            JOIN model.entity c ON c.id = st.id
            WHERE l1.range_id IN %s
              AND a.openatlas_class_name = 'place'
            GROUP BY c.name
            ORDER BY count DESC
            LIMIT 6
        """
        g.openatlas_cursor.execute(st_sql, (cs_tuple,))
        site_types = [
            {'name': row['name'], 'count': row['count']}
            for row in g.openatlas_cursor.fetchall()]

        # 3. Fundkategorien (Top 6 Standard-Typen)
        art_sql = """
            WITH RECURSIVE standard_types AS (
                SELECT h.id AS id
                FROM web.hierarchy h
                WHERE h.category = 'standard'
                UNION ALL
                SELECT l.domain_id AS id
                FROM model.link l
                JOIN standard_types st ON l.range_id = st.id
                WHERE l.property_code = 'P127'
            )
            SELECT c.name AS name, COUNT(DISTINCT a.id) AS count
            FROM model.entity a
            JOIN model.link l1 ON l1.domain_id = a.id
                AND l1.property_code = 'P2'
            JOIN model.link l2 ON l2.domain_id = a.id
                AND l2.property_code = 'P2'
            JOIN standard_types st ON st.id = l2.range_id
            JOIN model.entity c ON c.id = st.id
            WHERE l1.range_id IN %s
              AND a.openatlas_class_name = 'artifact'
            GROUP BY c.name
            ORDER BY count DESC
            LIMIT 6
        """
        g.openatlas_cursor.execute(art_sql, (cs_tuple,))
        artifact_types = [
            {'name': row['name'], 'count': row['count']}
            for row in g.openatlas_cursor.fetchall()]

        # 4. Klassen-Zählung für alle OpenAtlas-Klassen
        kpi_sql = """
            SELECT e.openatlas_class_name, COUNT(*) AS count
            FROM model.entity e
            JOIN model.link l1 ON l1.domain_id = e.id
                AND l1.property_code = 'P2'
            WHERE l1.range_id IN %s
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
            'class_counts': kpi_counts,
            'kpis': {
                'places': kpi_counts.get('place', 0),
                'features': kpi_counts.get('feature', 0),
                'artifacts': kpi_counts.get('artifact', 0),
                'human_remains': kpi_counts.get('human_remains', 0),
                'references': kpi_counts.get('bibliography', 0),
                'files': kpi_counts.get('file', 0)}}
    except Exception:
        return default_stats


def _resolve_localized_text(value: Any) -> str:
    """Löst mehrsprachige JSON-Objekte oder Strings auf."""
    if isinstance(value, str):
        return value
    if isinstance(value, dict) and value:
        lang = getattr(g, 'language', None)
        pref = getattr(g, 'preferred_language', 'en')
        return (
            value.get(lang)
            or value.get(pref)
            or value.get('en')
            or next(iter(value.values()), ''))
    return ''


def build_dynamic_landing_sections(
        landing_stats: dict[str, Any],
        view_class_count: dict[str, Any],
        predefined_filters: list[dict[str, Any]] | None = None) -> tuple[
            list[dict[str, Any]], list[dict[str, Any]]]:
    """Erstellt dynamische KPI- und Themenkacheln für die Startseite.

    Berücksichtigt für die KPI-Kacheln die im Backend konfigurierten
    `shown_classes` und `hidden_classes` und erstellt die Themenkacheln
    anhand der im Backend gespeicherten `predefined_filters`.
    """
    settings = getattr(g, 'settings', None)
    shown = set(settings.shown_classes) if settings else set()
    hidden = set(settings.hidden_classes) if settings else set()
    active_classes = shown - hidden

    view_classes = getattr(
        g, 'view_classes', app.config.get('VIEW_CLASSES', {}))
    db_counts: dict[str, int] = landing_stats.get('class_counts', {})

    # Fallback counts from view_class_count subunits
    api_counts: dict[str, int] = {}
    for vc_data in (view_class_count or {}).values():
        for subunit in vc_data.get('subunits', []):
            for cls_name, cnt in subunit.items():
                api_counts[cls_name] = cnt

    kpi_cards: list[dict[str, Any]] = []
    thematic_cards: list[dict[str, Any]] = []

    for view_class, class_tuple in view_classes.items():
        group_active_classes = [
            cls for cls in class_tuple if cls in active_classes]
        if not group_active_classes:
            continue

        for cls in group_active_classes:
            count = db_counts.get(cls, api_counts.get(cls, 0))
            if count <= 0:
                continue
            meta = CLASS_KPI_META.get(cls, {
                'label': cls.replace('_', ' ').capitalize(),
                'icon': 'bi-archive',
                'image': 'item.png',
                'color_key': view_class,
                'tab': view_class})
            kpi_cards.append({
                'class_name': cls,
                'view_class': view_class,
                'label': meta['label'],
                'icon': meta['icon'],
                'image': meta['image'],
                'color_key': meta['color_key'],
                'tab': meta['tab'],
                'count': count})

    if predefined_filters is None:
        predefined_filters = getattr(g, 'predefined_filters', []) or []

    palette_tabs = list(VIEW_CLASS_META.keys())
    for idx, pf in enumerate(predefined_filters):
        title = _resolve_localized_text(pf.get('label'))
        if not title:
            continue
        description = _resolve_localized_text(pf.get('description'))
        tabs = [
            t for t in (pf.get('tabs') or [])
            if isinstance(t, str) and t.strip()]
        fp = pf.get('filter_parameters') or {}
        fp_classes = fp.get('classes') or []

        if tabs:
            primary_tab = tabs[0]
        elif fp_classes and fp_classes[0] in CLASS_KPI_META:
            primary_tab = CLASS_KPI_META[fp_classes[0]]['tab']
        else:
            primary_tab = palette_tabs[idx % len(palette_tabs)]

        vc_meta = VIEW_CLASS_META.get(primary_tab, {
            'btn_class': 'btn-outline-secondary',
            'icon': 'bi-bookmark-star',
            'image': 'item.png'})

        icon_data = pf.get('icon')
        if (isinstance(icon_data, dict)
                and icon_data.get('type') == 'css'
                and icon_data.get('value')):
            raw_icon = str(icon_data['value']).strip()
            icon_type = 'css'
            icon_value = raw_icon if 'bi ' in raw_icon else f'bi {raw_icon}'
        elif (isinstance(icon_data, dict)
                and icon_data.get('type') == 'img'
                and icon_data.get('value')):
            raw_img = str(icon_data['value']).strip()
            icon_type = 'img'
            icon_value = f'/static/images/icons/{raw_img}'
        else:
            if len(fp_classes) == 1 and fp_classes[0] in CLASS_KPI_META:
                fallback_img = CLASS_KPI_META[fp_classes[0]]['image']
            else:
                fallback_img = vc_meta['image']
            icon_type = 'img'
            icon_value = f'/static/images/entity_icons/{fallback_img}'

        tab_buttons: list[dict[str, str]] = []
        for t in tabs:
            t_meta = VIEW_CLASS_META.get(t, {
                'tab_label': t.capitalize(),
                'btn_class': 'btn-outline-secondary',
                'icon': 'bi-arrow-right'})
            tab_buttons.append({
                'tab': t,
                'label': t_meta.get('tab_label', t.capitalize()),
                'icon': t_meta.get('icon', 'bi-arrow-right'),
                'btn_class': t_meta.get(
                    'btn_class', 'btn-outline-secondary')})

        thematic_cards.append({
            'id': pf.get('id'),
            'title': title,
            'description': description,
            'view_class': primary_tab,
            'target_tab': tabs[0] if tabs else None,
            'tabs': tabs,
            'tab_buttons': tab_buttons,
            'icon_type': icon_type,
            'icon_value': icon_value,
            'btn_class': vc_meta['btn_class'],
            'button_label': _l('Explore topic')})

    return kpi_cards, thematic_cards


def _format_getdates_value(raw_date: Any) -> str:
    """Formatiert einen `tng.getdates`-Rohstring (z.B. `000000600-01-01`)."""
    if not raw_date:
        return ''
    date_str = str(raw_date).strip()
    if not date_str:
        return ''

    is_bc = date_str.startswith('-')
    clean_str = date_str.lstrip('-').strip()
    parts = clean_str.split('-')

    try:
        year = int(parts[0])
    except ValueError:
        return date_str

    era = ' BC' if is_bc else ''
    if len(parts) < 3:
        return f'{year}{era}'

    month_str, day_str = parts[1], parts[2]
    if (month_str, day_str) in (('01', '01'), ('12', '31')):
        return f'{year}{era}'

    try:
        month = int(month_str)
        day = int(day_str)
        return f'{day:02d}.{month:02d}.{year}{era}'
    except ValueError:
        return f'{year}{era}'


def _format_timespan(begin_raw: Any, end_raw: Any) -> str:
    """Formatiert Start- und Enddatum zu einer lesbaren Zeitspanne."""
    begin_label = _format_getdates_value(begin_raw)
    end_label = _format_getdates_value(end_raw)
    if begin_label and end_label:
        if begin_label == end_label:
            return begin_label
        return f'{begin_label} – {end_label}'
    return begin_label or end_label


@cache.memoize(timeout=86400)
def get_landing_sites_geojson(
        case_study_ids: tuple[int, ...],
        limit: int = 5000,
        cache_version: int = 2) -> dict[str, Any]:
    """Erstellt ein leichtgewichtiges GeoJSON aller Fundorte für die Karte.

    Args:
        case_study_ids: Tuple von Fallstudien-IDs zur Filterung.
        limit: Maximale Anzahl von Fundorten.
        cache_version: Versionsschlüssel zur Cache-Invalidierung.

    Returns:
        GeoJSON FeatureCollection Dictionary.
    """
    _ = cache_version
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
                CASE
                    WHEN e.begin_comment LIKE '-%'
                    THEN TO_CHAR(e.begin_comment::INTEGER, 'FM000000000')
                    WHEN EXTRACT(
                        YEAR FROM LEAST(e.begin_from, e.begin_to)::DATE) < 1
                    THEN '-' || TO_CHAR(
                        LEAST(e.begin_from, e.begin_to),
                        'FM00000YYYY-MM-DD')
                    ELSE TO_CHAR(
                        LEAST(e.begin_from, e.begin_to),
                        'FM00000YYYY-MM-DD')
                END AS begin,
                CASE
                    WHEN e.end_comment LIKE '-%'
                    THEN TO_CHAR(e.end_comment::INTEGER, 'FM000000000')
                    WHEN EXTRACT(
                        YEAR FROM LEAST(e.end_to, e.end_from)::DATE) < 1
                    THEN '-' || TO_CHAR(
                        LEAST(e.end_to, e.end_from),
                        'FM00000YYYY-MM-DD')
                    ELSE TO_CHAR(
                        LEAST(e.end_to, e.end_from),
                        'FM00000YYYY-MM-DD')
                END AS end
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
            date_label = _format_timespan(r['begin'], r['end'])

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
