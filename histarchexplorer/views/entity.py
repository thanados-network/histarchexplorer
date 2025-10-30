import json
import time
from collections import defaultdict
from dataclasses import asdict
from typing import Any, Optional

from flask import abort, g, render_template

from histarchexplorer import app
from histarchexplorer.api.presentation_view import (
    EntityTypeModel, File, PresentationView, Relation)
from histarchexplorer.database.entity import (
    check_if_place_hierarchy, get_first_geom)
from histarchexplorer.utils.view_util import get_cite_button
from histarchexplorer.views.entities import get_browse_list_entities
from histarchexplorer.views.views import type_tree


@app.route('/entity/<int:id_>')
@app.route('/entity/<int:id_>/<tab_name>')
def entity_view(id_: int, tab_name: str = "overview") -> str:
    sidebar_elements = app.config['SIDEBAR_OPTIONS']
    if tab_name not in {item['route'] for item in sidebar_elements}:
        abort(404)
    entity = PresentationView.from_api(id_)
    hierarchy = {
        'subs': get_sub_count(entity),
        'root': get_hierarchy(entity)}
    for p in hierarchy['root']:
        print("---")
        print(p)
    overview_map_geometry = entity.geometry_json
    if not overview_map_geometry:
        if hierarchy.get('root'):
            overview_map_geometry = get_parent_geometry(hierarchy['root'])
        else:
            overview_map_geometry = {
                'type': 'FeatureCollection',
                'features': get_features_for_map(entity)}

    data: dict[str, Any] = {
        'entity': asdict(entity),
        'spatial': {
            'type': 'FeatureCollection',
            'features': get_features_for_map(entity, hierarchy)},
        'overview_map': overview_map_geometry}

    return render_template(
        'entity.html',
        sidebar_elements=build_sidebar(id_, sidebar_elements),
        data=data,
        page_name="landing",
        active_tab=tab_name,
        entity_id=id_)


def get_entity_images(files: list[File]) -> tuple[
    File, list[File], list[File]]:
    images = []
    main_image = None
    for image in files:
        if image.render_type in ['unknown', 'webp']:
            continue
        if image.main_image:
            main_image = image
        else:
            images.append(image)

    if not main_image and images:
        main_image = images.pop(0)
    initial_images = images[:2]
    images.append(main_image)
    return main_image, initial_images, images


@app.route('/get_entity/<int:id_>/<tab_name>')
def get_entity(id_: int, tab_name=None) -> str:
    if tab_name == 'subunits':
        subunit_data = get_browse_list_entities(id_)
        filtered_view_classes = {
            key: tuple(list(d.keys())[0] for d in value)
            for key, value in subunit_data['counts'].items()}

        return render_template(
            f'tabs/browse.html',
            subunits=True,
            view_classes=filtered_view_classes,
            subunit_data=subunit_data,
            active_tab=tab_name,
            typetree_data=type_tree().json,
            main_image_json=g.main_images,
            tab_name='subunits')

    entity = PresentationView.from_api(id_)
    hierarchy = {
        'subs': get_sub_count(entity),
        'root': get_hierarchy(entity)}

    overview_map_geometry = entity.geometry_json
    if not overview_map_geometry:
        if hierarchy.get('root'):
            overview_map_geometry = get_parent_geometry(hierarchy['root'])
        else:
            overview_map_geometry = {
                'type': 'FeatureCollection',
                'features': get_features_for_map(entity)}
    data: dict[str, Any] = {
        'overview_map': json.dumps(overview_map_geometry)}

    main_image, initial_images, images = get_entity_images(entity.files)

    match tab_name:
        case 'feature':  # pragma: no cover
            pass
        case 'map':
            pass
        case 'media':
            pass
        case 'overview':
            pass
        case _ if tab_name not in ['feature']:
            abort(404)

    return render_template(
        f'tabs/{tab_name}.html',
        data=json.dumps(data),
        entity=entity,
        categorized_types=get_categorized_types(entity.types),
        images=images,
        main_image=main_image,
        initial_images=initial_images,
        cite_button=get_cite_button(entity),
        hierarchy=hierarchy,
        overview_map_geometry=overview_map_geometry)


def get_features_for_map(
        e: PresentationView,
        hierarchy: Optional[dict[str, Any]] = None) \
        -> list[Optional[dict[str, Any]]]:
    map_data = []
    first_geom = None
    if e.geometry_json:
        map_data.extend(
            adapt_map_dict(
                e.geometry_json, e.title, e.id, e.system_class, e.id))
    elif hierarchy:
        first_geom = get_parent_geometry_id(hierarchy['root'])

    for k in ['place',
              'feature',
              'stratigraphic_unit',
              'artifact',
              'human_remains']:
        for rel in e.relations.get(k, []):
            if rel.geometry_json:
                map_data.extend(adapt_map_dict(
                    rel.geometry_json,
                    rel.name,
                    rel.id,
                    rel.system_class,
                    first_geom))
    return map_data


def check_sidebar_elements(tab: str, id_: int) -> bool:
    match tab:
        case 'map':
            return bool(get_first_geom(id_))
        case 'subunits':
            return bool(check_if_place_hierarchy(id_))
        case 'overview' | 'media':
            return True
        case _:
            return False


def build_sidebar(id_: int, sidebar_elements: dict[str, Any]):
    return sorted(
        (item for item in sidebar_elements if check_sidebar_elements(
            item.get('route'), id_)),
        key=lambda item: item['order'])


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
        first_geom: Optional[int] = None) -> list[dict[str, Any]]:
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
            {'type': type_, 'icon': type_.division['icon']})
    sorted_divisions = dict(sorted(divisions.items(), key=sort_key))
    return sorted_divisions


def get_hierarchy(main_entity: PresentationView) -> list[Relation | None]:
    root = []
    match main_entity.system_class:
        case 'feature':
            if 'place' in main_entity.relations and main_entity.relations[
                'place']:  # nur wenn dict key place hat und liste nicht leer
                # Bernhard: Wann passiert es, dass ein feature keinen Place
                # hat? Das darf nicht vorkommen.
                root.append(main_entity.relations['place'][0])
        case 'stratigraphic_unit':
            for feature in main_entity.relations.get('feature', []):
                for relation in feature.relation_types:
                    if relation['relationTo'] == main_entity.id:
                        root.append(feature)
            if 'place' in main_entity.relations and main_entity.relations[
                'place']:
                # Bernhard: Kann mir bitte jemand sagen, wann das vorkommt?
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
            if 'place' in main_entity.relations and main_entity.relations[
                'place']:
                root.append(main_entity.relations['place'][0])
    root.reverse()
    return root


def get_sub_count(main_entity: PresentationView) -> int:
    count = 0
    # It was not wished to show all subunits, only direct ones
    # sub_relations_map = {
    #    'place': ['feature', 'stratigraphic_unit', 'artifact',
    #              'human_remains'],
    #    'feature': ['stratigraphic_unit', 'artifact', 'human_remains'],
    #    'stratigraphic_unit': ['artifact', 'human_remains'],
    #    'artifact': ['artifact'],
    #    'human_remains': ['human_remains']}
    sub_relations_map = {
        'place': ['feature'],
        'feature': ['stratigraphic_unit'],
        'stratigraphic_unit': ['artifact', 'human_remains'],
        'artifact': ['artifact'],
        'human_remains': ['human_remains']}
    for rel_type in sub_relations_map.get(main_entity.system_class, []):
        count += len(main_entity.relations.get(rel_type, []))
    return count


def get_files_for_id(id: int) -> dict[str, list[str]]:
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
                  AND l.range_id = %(id)s
                  AND l.property_code = 'P67') a; \
          """

    g.cursor.execute(sql, {'id': id})
    result = g.cursor.fetchone()
    if result:
        return result
    return None


@app.route('/get_rastermaps/<int:id>')
def get_rastermaps(id: int) -> str:
    return json.dumps(get_files_for_id(id))
