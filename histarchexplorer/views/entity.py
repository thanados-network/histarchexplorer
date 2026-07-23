import json
import threading
import time
from collections import defaultdict
from dataclasses import asdict
from typing import Any, Optional

from flask import abort, g, render_template, request

from histarchexplorer import app
from histarchexplorer.api.api_access import ApiAccess
from histarchexplorer.api.presentation_view import (
    EntityTypeModel, File, PresentationView, Relation)
from histarchexplorer.api.util import get_description_translated
from histarchexplorer.utils.view_util import (
    get_cite_button, get_refresh_button)
from histarchexplorer.views.entities import get_browse_list_entities
from histarchexplorer.views.views import type_tree


@app.route('/entity/<int:id_>')
@app.route('/entity/<int:id_>/<tab_name>')
def entity_view(id_: int, tab_name: str = "overview") -> str:
    """Render the presentation layout for a single entity.

    Sets up the sidebar navigation options and returns the main HTML
    template populated with details for the entity.
    """
    data = entity_data(id_)
    entity_dict = data['entity']
    has_feature = (entity_dict.get('system_class') == 'feature' or
                   bool(entity_dict.get('relations', {}).get('feature')))
    sidebar = app.config['SIDEBAR_OPTIONS']
    if not has_feature:
        sidebar = [
            item for item in sidebar if item['route'] != 'catalogue']
    if tab_name not in {item['route'] for item in sidebar}:
        abort(404)
    return render_template(
        'entity.html',
        sidebar_elements=sorted(sidebar, key=lambda item: item['order']),
        data=data,
        page_name="landing",
        active_tab=tab_name,
        entity_id=id_)


def get_entity_images(
        files: list[File]) \
        -> tuple[File | None, list[File | None], list[File | None]]:
    images = []
    main_image = None
    for image in files:
        if image.render_type in ['unknown', 'webp']:
            continue
        # Skip images inherited from a super entity. The frontend
        # filters these out anyway (`from_super_entity === false`), and an
        # inherited `main_image` would otherwise override the entity's own
        # one, leaving no displayable image.
        if image.from_super_entity:
            continue
        if image.main_image:
            main_image = image
        else:
            images.append(image)

    if not main_image and images:
        main_image = images.pop(0)
    initial_images = images[:g.additional_files_for_overview]
    if main_image:
        images.append(main_image)
    return main_image, initial_images, images


def is_part_of(relation: Relation, parent_id: int) -> bool:
    """Check if a relation forms part of the given parent entity."""
    for rel_type in relation.relation_types or []:
        if (rel_type.get('relationTo') == parent_id
                and rel_type.get('property') == 'crm:P46i_forms_part_of'):
            return True
    return False


def extract_year(date_str: Optional[str]) -> Optional[int]:
    """Extract the (signed) year from an ISO date string.

    Negative values represent BC years.
    """
    if not date_str:
        return None
    date_part = date_str.split("T")[0]
    is_bc = date_part.startswith("-")
    year_part = date_part.lstrip("-").split("-")[0]
    if not year_part.isdigit():
        return None
    year = int(year_part)
    return -year if is_bc else year


def compact_year_span(view: PresentationView) -> Optional[str]:
    """Build a shortened time span from earliest begin to latest end.

    Only the year is kept; BC/AD eras are appended.
    """
    begin = None
    end = None
    if view.when and view.when.start:
        begin = view.when.start.earliest or view.when.start.latest
    if view.when and view.when.end:
        end = view.when.end.latest or view.when.end.earliest

    def fmt(year: Optional[int]) -> Optional[str]:
        if year is None:
            return None
        return f"{abs(year)} {'BC' if year < 0 else 'AD'}"

    year_from = fmt(extract_year(begin))
    year_to = fmt(extract_year(end))
    if year_from and year_to:
        if year_from == year_to:
            return year_from
        return f"{year_from} – {year_to}"
    return year_from or year_to


def get_valid_images(view: PresentationView) -> list[File]:
    """Collect displayable images for an entity.

    Excludes inherited (`from_super_entity`) files and non-image
    render types. No placeholder fallback is added.
    """
    images = []
    main_image = None
    for image in view.files:
        if image.from_super_entity:
            continue
        if image.render_type not in ('image', 'svg'):
            continue
        if not (image.iiif_base_path or image.url):
            continue
        if image.main_image:
            main_image = image
        else:
            images.append(image)
    if main_image:
        images.insert(0, main_image)
    return images


def build_sidebar_block(view: PresentationView) -> dict[str, Any]:
    """Build a uniform detail block for the map sidebar.

    Used identically for the feature, stratigraphic units, artifacts
    and human remains.
    """
    return {
        'id': view.id,
        'title': view.title,
        'system_class': view.system_class,
        'year_span': compact_year_span(view),
        'main_types': [t for t in view.types if t.is_standard],
        'categorized_types': get_categorized_types(view.types),
        'description': view.description,
        'images': get_valid_images(view)}


def _subunit_items(entity: dict[str, Any], keys: tuple[str, ...]) \
        -> list[dict[str, Any]]:
    """Return the first valid ordered child collection from an entity."""
    for key in keys:
        items = entity.get(key)
        if isinstance(items, list):
            return [item for item in items if isinstance(item, dict)]
    return []


def _subunit_description(value: Any) -> dict[str, str] | None:
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        return get_description_translated(value)
    return None


def _subunit_types(data: Any) -> list[EntityTypeModel]:
    """Parse type cards while discarding malformed upstream entries."""
    if not isinstance(data, list):
        return []
    types = []
    for raw_type in data:
        if not isinstance(raw_type, dict) or 'id' not in raw_type:
            continue
        type_data = raw_type.copy()
        if not isinstance(type_data.get('typeHierarchy'), list):
            type_data['typeHierarchy'] = []
        try:
            types.extend(PresentationView.parse_types([type_data]))
        except (TypeError, ValueError, KeyError) as error:
            app.logger.warning('Ignoring malformed subunits type: %s', error)
    return types


def _subunit_block(entity: dict[str, Any]) -> dict[str, Any] | None:
    """Convert one subunits entity card to the existing template contract."""
    id_ = entity.get('id')
    title = entity.get('title')
    system_class = entity.get('systemClass')
    if not isinstance(id_, int) or not isinstance(title, str):
        app.logger.warning('Ignoring malformed subunits entity card')
        return None
    if system_class not in {
            'feature', 'stratigraphic_unit', 'artifact', 'human_remains'}:
        app.logger.warning('Ignoring unsupported subunits class: %s',
                           system_class)
        return None
    when = PresentationView.parse_time_range(entity.get('when'))
    files = PresentationView.parse_file(entity.get('files', []))
    types = _subunit_types(entity.get('types'))
    return {
        'id': id_,
        'title': title,
        'system_class': system_class,
        'year_span': compact_year_span(
            PresentationView(
                id=id_, system_class=system_class, view_class='', title=title,
                description=None, aliases=None, start=None, end=None,
                when=when)),
        'main_types': [type_ for type_ in types if type_.is_standard],
        'categorized_types': get_categorized_types(types),
        'description': _subunit_description(entity.get('description')),
        'images': get_valid_images(
            PresentationView(
                id=id_, system_class=system_class, view_class='', title=title,
                description=None, aliases=None, start=None, end=None,
                files=files))}


def _subunits_graph_nodes(data: dict[str, Any]) -> dict[int, dict[str, Any]]:
    """Index the flat node graph returned by the subunits endpoint."""
    nodes = {}
    for items in data.values():
        if not isinstance(items, list):
            continue
        for item in items:
            if isinstance(item, dict) and isinstance(item.get('id'), int):
                nodes[item['id']] = item
    return nodes


def _subunits_graph_files(data: Any) -> list[dict[str, Any]]:
    """Adapt public subunits media records to presentation-view files."""
    if not isinstance(data, list):
        return []
    files = []
    for file_ in data:
        if not isinstance(file_, dict):
            continue
        file_data = file_.copy()
        if not isinstance(file_data.get('url'), str) and not isinstance(
                file_data.get('IIIFBasePath'), str):
            continue
        file_data['title'] = file_data.get('title') or file_data.get('name')
        file_data['publicShareable'] = True
        file_data['license'] = file_data.get('license') or 'public'
        file_data['fromSuperEntity'] = False
        files.append(file_data)
    return files


def _subunits_graph_card(node: dict[str, Any]) -> dict[str, Any] | None:
    """Adapt a flat graph node to the existing subunits card input."""
    properties = node.get('properties')
    if not isinstance(properties, dict):
        properties = {}
    types = []
    standard_type = properties.get('standardType')
    if isinstance(standard_type, dict):
        types.append({
            'id': standard_type.get('id'),
            'title': standard_type.get('name'),
            'descriptions': standard_type.get('description'),
            'isStandard': True,
            'typeHierarchy': standard_type.get('typeHierarchy', [])})
    raw_types = properties.get('types')
    if not isinstance(raw_types, list):
        raw_types = []
    for type_ in raw_types:
        if not isinstance(type_, dict):
            continue
        types.append({
            'id': type_.get('id'),
            'title': type_.get('name'),
            'descriptions': type_.get('description'),
            'isStandard': False,
            'typeHierarchy': type_.get('typeHierarchy', []),
            'value': type_.get('value'),
            'unit': type_.get('unit')})
    timespan = properties.get('timespan')
    when = {}
    if isinstance(timespan, dict):
        when = {
            'start': {
                'earliest': timespan.get('earliestBegin'),
                'latest': timespan.get('latestBegin')},
            'end': {
                'earliest': timespan.get('earliestEnd'),
                'latest': timespan.get('latestEnd')}}
    return _subunit_block({
        'id': node.get('id'),
        'title': properties.get('name'),
        'systemClass': node.get('openatlasClassName'),
        'description': properties.get('description'),
        'when': when,
        'types': types,
        'files': _subunits_graph_files(properties.get('files'))})


def _graph_children(
        node: dict[str, Any],
        nodes: dict[int, dict[str, Any]],
        system_class: str) -> list[dict[str, Any]]:
    """Return ordered children of one class from a flat subunits graph."""
    children = []
    child_ids = node.get('children')
    if not isinstance(child_ids, list):
        return children
    for child_id in child_ids:
        child = nodes.get(child_id)
        if child and child.get('openatlasClassName') == system_class:
            children.append(child)
    return children


def _normalize_subunits_graph(data: dict[str, Any]) -> list[dict[str, Any]]:
    """Build the template hierarchy from the endpoint's flat node graph."""
    nodes = _subunits_graph_nodes(data)
    hierarchy = []
    for root in nodes.values():
        for feature_data in _graph_children(root, nodes, 'feature'):
            feature = _subunits_graph_card(feature_data)
            if not feature:
                continue
            groups = []
            for su_data in _graph_children(
                    feature_data, nodes, 'stratigraphic_unit'):
                su = _subunits_graph_card(su_data)
                if not su:
                    continue
                children = []
                for system_class in ('artifact', 'human_remains'):
                    for child_data in _graph_children(
                            su_data, nodes, system_class):
                        child = _subunits_graph_card(child_data)
                        if child:
                            children.append(child)
                groups.append({'su': su, 'children': children})
            hierarchy.append({'feature': feature, 'groups': groups})
    return hierarchy


def normalize_subunits_data(data: dict[str, Any]) -> list[dict[str, Any]]:
    """Normalize an ordered `features → subunits → children` response."""
    if not isinstance(data, dict):
        return []
    if not isinstance(data.get('features'), list):
        return _normalize_subunits_graph(data)
    features = _subunit_items(data, ('features',))
    if data.get('systemClass') == 'feature':
        features = [data]
    hierarchy = []
    for feature_data in features:
        feature = _subunit_block(feature_data)
        if not feature or feature['system_class'] != 'feature':
            continue
        groups = []
        for su_data in _subunit_items(
                feature_data,
                ('subunits', 'stratigraphicUnits', 'stratigraphic_units')):
            su = _subunit_block(su_data)
            if not su or su['system_class'] != 'stratigraphic_unit':
                continue
            children = []
            for child_data in _subunit_items(
                    su_data,
                    ('children', 'artifacts', 'humanRemains', 'human_remains')):
                child = _subunit_block(child_data)
                if child and child['system_class'] in {
                        'artifact', 'human_remains'}:
                    children.append(child)
            groups.append({'su': su, 'children': children})
        hierarchy.append({'feature': feature, 'groups': groups})
    return hierarchy


def get_subunits_root_id(id_: int) -> int:
    """Return the place ID required by the subunits endpoint."""
    hierarchy = get_hierarchy(PresentationView.from_api(id_))
    if hierarchy:
        return hierarchy[-1].id
    return id_


def get_map_sidebar_data(id_: int) -> dict[str, Any]:
    """Assemble the hierarchical view-model for the map sidebar.

    Selects the clicked feature from the shared hierarchy response.
    """
    root_id = get_subunits_root_id(id_)
    hierarchy = normalize_subunits_data(ApiAccess.get_subunits(root_id))
    for item in hierarchy:
        if item['feature']['id'] == id_:
            return item
    return {}


def get_catalogue_data(id_: int) -> list[dict[str, Any]]:
    """Assemble the hierarchical view-model for the catalogue.

    Returns the cached hierarchy's features, stratigraphic units, artifacts,
    and human remains.
    """
    root_id = get_subunits_root_id(id_)
    return normalize_subunits_data(ApiAccess.get_subunits(root_id))


@app.route('/get_entity/<int:id_>/<tab_name>')
def get_entity(id_: int, tab_name: str) -> str:
    """Fetch content for a specific tab of an entity.

    Handles template loading for subunits, maps, media, features,
    or general overview sections of an archaeological item.
    """
    if tab_name == 'subunits':
        subunit_data = get_browse_list_entities(id_)
        filtered_view_classes = {
            key: tuple(list(d.keys())[0] for d in value)
            for key, value in subunit_data['counts'].items()}

        return render_template(
            'tabs/browse.html',
            subunits=True,
            filtered_view_classes=filtered_view_classes,
            subunit_data=subunit_data,
            active_tab=tab_name,
            typetree_data=type_tree().json,
            tab_name='subunits')

    match tab_name:
        case 'feature':
            sidebar = get_map_sidebar_data(id_)
            if not sidebar:
                abort(404)
            return render_template(
                'tabs/feature.html',
                sidebar=sidebar)
        case 'catalogue':
            catalogue_data = get_catalogue_data(id_)
            if not catalogue_data:
                abort(404)
            return render_template(
                'tabs/catalog.html',
                catalogue=catalogue_data)
        case 'map':
            pass
        case 'media':
            pass
        case 'overview':
            pass
        case _ if tab_name not in ['feature', 'catalogue']:
            abort(404)

    return render_template(f'tabs/{tab_name}.html', id_=id_, count=0)


def get_features_for_map(
        e: PresentationView,
        hierarchy: Optional[dict[str, Any]] = None) \
        -> list[dict[str, str | int] | None]:
    """Extract map features of an entity and its relations.

    Collects geometries from the entity and related child items,
    formatting them for map visualization in the frontend.
    """
    map_data: list[Optional[dict[str, str | int]]] = []
    first_geom = None
    if e.geometry_json:
        map_data.extend(
            adapt_map_dict(
                e.geometry_json, e.title, e.id, e.system_class, e.id))
    elif hierarchy:
        first_geom = get_parent_geometry_id(hierarchy['root'])

    sub_relations = [
        'place',
        'feature',
        'stratigraphic_unit',
        'artifact',
        'human_remains']
    for k in sub_relations:
        for rel in e.relations.get(k, []):
            if rel.geometry_json:
                map_data.extend(adapt_map_dict(
                    rel.geometry_json,
                    rel.name,
                    rel.id,
                    rel.system_class,
                    first_geom))
    return map_data


def get_parent_geometry(hierarchy: list[Relation]) -> dict[str, Any]:
    for root_element in reversed(hierarchy):
        if root_element.geometries:
            return root_element.geometry_json
    return {}


def get_parent_geometry_id(hierarchy: list[Relation]) -> int | None:
    id_ = None
    for root_element in reversed(hierarchy):
        if root_element.geometries:
            id_ = root_element.id
            break
    return id_


def adapt_map_dict(
        geom: dict[str, Any],
        name: str,
        id_: int,
        system_class: str,
        first_geom: Optional[int] = None) -> list[dict[str, str | int]]:
    features = []
    if geom.get('type') == 'FeatureCollection':
        features.extend(geom['features'])
    else:
        features.append(geom)
    output = []
    for feature in features:
        if '(autogenerated)' in feature['properties']['title']:
            continue
        if first_geom == int(id_):
            feature['properties']['main'] = True
        feature['properties']['class'] = system_class
        feature['properties']['label'] = name
        feature['properties']['id'] = int(id_)
        output.append(feature)

    return output


def get_categorized_types(
        types: list[EntityTypeModel]) -> dict[str, list[EntityTypeModel]]:
    def sort_key(item: tuple[str, list]) -> tuple[int, str]:
        key = item[0]
        match key:
            case 'case_study':
                return 0, key
            case 'other':
                return 2, key
            case _:
                return 1, key

    divisions = defaultdict(list)
    for type_ in types:
        if type_.is_standard:
            continue
        label = type_.division['label'].replace(' ', '_')
        divisions[label].append(
            {'type': type_, 'division': type_.division})
    sorted_divisions = dict(sorted(divisions.items(), key=sort_key))
    return sorted_divisions


def get_hierarchy(main_entity: PresentationView) -> list[Relation | None]:
    """Determine the administrative hierarchy of an entity.

    Walks relationships to identify parent units (e.g., matching
    stratigraphic units, features, and places) in reversed order.
    """
    root: list[Optional[Relation]] = []
    match main_entity.system_class:
        case 'feature':
            if ('place' in main_entity.relations
                    and main_entity.relations['place']):
                root.append(main_entity.relations['place'][0])
        case 'stratigraphic_unit':
            for feature in main_entity.relations.get('feature', []):
                for relation in feature.relation_types:
                    if relation['relationTo'] == main_entity.id:
                        root.append(feature)
            if ('place' in main_entity.relations
                    and main_entity.relations['place']):
                root.append(main_entity.relations['place'][0])
        case 'artifact' | 'human_remains':
            stratigraphic_unit_id = None
            for feature in main_entity.relations.get('stratigraphic_unit', []):
                for relation in feature.relation_types:
                    if relation['relationTo'] == main_entity.id:
                        root.append(feature)
                        stratigraphic_unit_id = feature.id
            for feature in main_entity.relations.get('feature', []):
                for relation in feature.relation_types:
                    if relation['relationTo'] == stratigraphic_unit_id:
                        root.append(feature)
            if ('place' in main_entity.relations
                    and main_entity.relations['place']):
                root.append(main_entity.relations['place'][0])
    root.reverse()
    return root


def get_sub_count(main_entity: PresentationView) -> dict[str, int | list[int]]:
    """Count and gather IDs of sub-elements within an entity.

    Finds forms-part-of (crm:P46) relationship types, returning
    the total count and list of child IDs.
    """
    sub_relations_map = {
        'place': ['feature'],
        'feature': ['stratigraphic_unit'],
        'stratigraphic_unit': ['artifact', 'human_remains'],
        'artifact': ['artifact'],
        'human_remains': ['human_remains']}
    count = 0
    ids = []
    for rel_type in sub_relations_map.get(main_entity.system_class, []):
        for rel in main_entity.relations.get(rel_type, []):
            count += sum(
                1
                for rt in rel.relation_types
                if rt.get("relationTo") == main_entity.id
                and rt.get("property") == "crm:P46i_forms_part_of")
            for rt in rel.relation_types:
                if rt.get("relationTo") == main_entity.id \
                        and rt.get("property") == "crm:P46i_forms_part_of":
                    ids.append(rel.id)
    return {'count': count, 'ids': ids}


def get_files_for_ids(
        ids: list[int]) -> dict[str, list[dict[str, Any]]] | None:
    sql = """
          SELECT JSONB_AGG(
                         jsonb_build_object(
                                 'id', a.id,
                                 'name', a.name,
                                 'description', a.description,
                                 'bbox', a.bounding_box::JSONB
                         )
                 ) AS images
          FROM (SELECT e.id,
                       e.name,
                       e.description,
                       o.image_id,
                       o.bounding_box
                FROM model.entity e
                         JOIN model.link l ON e.id = l.domain_id
                         JOIN web.map_overlay o ON o.image_id = e.id
                WHERE e.openatlas_class_name = 'file'
                  AND l.range_id = ANY(%(ids)s)
                  AND l.property_code = 'P67') a;
          """

    g.openatlas_cursor.execute(sql, {'ids': ids})
    result = g.openatlas_cursor.fetchone()
    if result:
        return result
    return None


@app.route('/get_rastermaps', methods=['POST'])
def get_rastermaps() -> str:
    """Retrieve raster overlay maps for the requested entity IDs.

    Expects a JSON body containing a list of IDs and returns the
    associated map details.

    Input format:
        {
            "ids": [int, ...]
        }

    Output format:
        {
            "images": [
                {
                    "id": int,
                    "name": str,
                    "description": str,
                    "bbox": [
                        [float, float],
                        [float, float]
                    ]
                }
            ]
        }
    """
    data = request.get_json()
    if not data or 'ids' not in data:
        abort(400, "Missing 'ids' in request body")
    ids = data['ids']
    if not isinstance(ids, list):
        abort(400, "'ids' must be a list")
    return json.dumps(get_files_for_ids(ids))


@app.route('/presentation-view/<int:id_>')
def presentation_view(id_: int) -> dict[str, Any]:
    """Retrieve full presentation details for an entity as JSON.

    Converts the structured `PresentationView` model into a plain
    dictionary representation. This provides core historical, spatial,
    and semantic relationship data for UI widgets.

    Args:
        id_: int - The unique entity ID.

    Returns:
        dict: Serialized JSON structure matching the fields defined in
            the `PresentationView` class.
    """
    return asdict(PresentationView.from_api(id_))


@app.route('/entity-data/<int:id_>')
def entity_data(id_: int) -> dict[str, Any]:
    """Generate all contextual display data for an entity page.

    Aggregates spatial geometries, hierarchical relations, categorized
    types, and associated media files to drive the frontend entity details
    interface.

    Args:
        id_: int - The unique entity ID.

    Returns:
        dict: An ad-hoc dictionary with the following keys:
            - entity (dict): Serialized `PresentationView` structure.
            - spatial (dict): A GeoJSON FeatureCollection of map elements.
            - hierarchy (dict): Parent relationships and sub-counts.
            - overviewMap (dict): Geometry or FeatureCollection for mapping.
            - categorizedTypes (dict): Grouped classifications.
            - citeButton (str): Pre-rendered citation button HTML.
            - refreshButton (str): Pre-rendered cache refresh button HTML.
            - mainImage (dict | None): Primary image file metadata.
            - initialImage (list[dict]): Initial media thumbnails.
            - images (list[dict]): All public shareable file objects.
    """
    entity = PresentationView.from_api(id_)
    data = get_sub_count(entity)
    hierarchy = {
        'ids': data['ids'],
        'subs': data['count'],
        'root': get_hierarchy(entity)}
    overview_map_geometry = entity.geometry_json

    if not overview_map_geometry:
        if hierarchy.get('root'):
            overview_map_geometry = get_parent_geometry(hierarchy['root'])
        else:
            overview_map_geometry = {
                'type': 'FeatureCollection',
                'features': get_features_for_map(entity)}
    main_image, initial_images, images = get_entity_images(entity.files)

    external_identifiers_settings = {}
    for sys_id, data in g.settings.external_identifiers.items():
        resolved_data = data.copy()
        if data.get('icon_type') == 'img' and data.get('icon_value'):
            from histarchexplorer.api.util import get_icon_url
            resolved_data['icon_url'] = get_icon_url(data['icon_value'])
        external_identifiers_settings[sys_id] = resolved_data

    return {
        'entity': asdict(entity),
        'spatial': {
            'type': 'FeatureCollection',
            'features': get_features_for_map(entity, hierarchy)},
        'hierarchy': hierarchy,
        'overviewMap': overview_map_geometry,
        'categorizedTypes': get_categorized_types(entity.types),
        'citeButton': get_cite_button(entity),
        'refreshButton': get_refresh_button(entity.id) or "",
        'mainImage': main_image,
        'initialImage': initial_images,
        'images': images,
        'externalIdentifiersSettings': external_identifiers_settings}


def background_cache_relations(
        app_, entity_id: int, headers: dict, base_url: str) -> None:
    """Fetch and cache all related entities in the background.

    Iterates through semantic relations and triggers a full API fetch for
    each, memoizing them in Redis. Adds a 0.5s delay between requests.
    """
    print(f"DEBUG: Entering background_cache_relations for {entity_id}")
    try:
        with app_.test_request_context(base_url=base_url):
            print(f"DEBUG: Context established for {entity_id}")
            g.api_headers = headers
            try:
                print(entity_id, "background caching relations")
                entity = PresentationView.from_api(entity_id)
                related_ids = set()
                for relations in entity.relations.values():
                    for rel in relations:
                        if rel.id > 0:
                            related_ids.add(rel.id)

                for rid in related_ids:
                    try:
                        PresentationView.from_api(rid)
                        time.sleep(0.5)
                    except Exception as e:
                        app_.logger.error(
                            f"Failed to cache related entity {rid}: {e}")
            except Exception as e:
                app_.logger.error(
                    f"Background caching failed for {entity_id}: {e}")
    except Exception as e:
        print(f"DEBUG: Failed to start background task for {entity_id}: {e}")


@app.route('/api/cache-related/<int:id_>')
def cache_related(id_: int) -> str:
    """Initiate background caching for an entity's relations.

    Spawns a daemon thread to pre-fetch related entity data without
    blocking the current request.
    """
    print(f"API call received: /api/cache-related/{id_}")
    headers = getattr(g, 'api_headers', {})
    base_url = request.base_url
    thread = threading.Thread(
        target=background_cache_relations,
        args=(app, id_, headers, base_url))
    thread.daemon = True
    thread.start()
    return json.dumps({"status": "success"})
