import json
from collections import defaultdict
from typing import Any, Optional

from flask import abort, g, render_template

from histarchexplorer import app
from histarchexplorer.api.parser import Parser
from histarchexplorer.database.entity import (
    check_if_place_hierarchy, get_first_geom)
from histarchexplorer.models.entity import Entity
from histarchexplorer.models.presentation_view import (
    EntityTypeModel, PresentationView, Relation)
from histarchexplorer.utils.view_util import get_cite_button
from histarchexplorer.views.entities import get_browse_list_entities
from histarchexplorer.views.views import type_tree


@app.route('/entity/<int:id_>')
@app.route('/entity/<int:id_>/<tab_name>')
def entity(id_: int, tab_name: str = "overview") -> str:
    sidebar_elements = app.config['SIDEBAR_OPTIONS']
    if tab_name not in {item['route'] for item in sidebar_elements}:
        abort(404)
    return render_template(
        'entity.html',
        sidebar_elements=build_sidebar(id_, sidebar_elements),
        page_name="landing",
        active_tab=tab_name,
        entity_id=id_)


@app.route('/get_entity/<int:id_>/<tab_name>')
def get_entity(id_: int, tab_name=None) -> str:
    related_entities = {}
    catalogue_entities = []
    main_image = None
    initial_images = []
    feature = None

    main_entity = PresentationView.from_api(id_)
    categorized_types = get_categorized_types(main_entity.types)
    hierarchy = {
        'subs': get_sub_count(main_entity),
        'root': get_hierarchy(main_entity)}

    overview_map_geometry = main_entity.geometry_json
    if not overview_map_geometry:
        overview_map_geometry = get_parent_geometry(hierarchy['root'])
    data: dict[str, Any] = {
        'entity': main_entity.to_json(),
        'overview_map': json.dumps(overview_map_geometry)}
    match tab_name:
        case 'feature':
            # todo: core information about the feature are available in the
            #  main entity
            feature = Entity.get_entity(id_, Parser())

        case 'map':
            map_data = {
                'type': 'FeatureCollection',
                'features': get_features_for_map(main_entity, hierarchy)}
            if not map_data['features']:
                abort(404)
            data['spatial'] = map_data

        case 'overview':
            images = []
            for image in main_entity.files:
                if image.main_image:
                    main_image = image
                else:
                    images.append(image)

            if not main_image and images:
                main_image = images.pop(0)
            initial_images = images[:2]

        case 'media':
            pass

        case 'subunits':
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

        case _ if tab_name not in ['feature']:
            abort(404)

    return render_template(
        f'tabs/{tab_name}.html',
        data=json.dumps(data),
        entity=main_entity,
        categorized_types=categorized_types,
        features=feature,
        main_image=main_image,
        initial_images=initial_images,
        manifests=[img.iiif_manifest for img in main_entity.files],
        related_entities=related_entities or {},
        cite_button=get_cite_button(main_entity),
        catalogue_entities=catalogue_entities,
        hierarchy=hierarchy,
        overview_map_geometry=overview_map_geometry)


def get_features_for_map(
        e: PresentationView,
        hierarchy: dict[str, Any]) -> list[dict[str, Any]]:
    map_data = []
    first_geom = None
    if e.geometry_json:
        map_data.extend(
            adapt_map_dict(
                e.geometry_json, e.title, e.id, e.system_class, e.id))
    else:
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
        case 'overview':
            return True
        case 'media' | _:
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
    for root_element in reversed(hierarchy):
        if root_element.geometries:
            return root_element.id
    return None


def adapt_map_dict(
        geom: dict[str, Any] | None,
        name: str,
        id_: int,
        system_class: str,
        first_geom: Optional[int] = None) -> list[dict[str, Any]]:
    if not geom:
        return []
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
