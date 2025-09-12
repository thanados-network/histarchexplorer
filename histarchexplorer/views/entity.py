
import json
from collections import defaultdict
from dataclasses import asdict
from typing import Any, Dict, List, Optional

from flask import abort, g, render_template

from histarchexplorer import app
from histarchexplorer.api.parser import Parser
from histarchexplorer.models.depiction import Depiction
from histarchexplorer.models.entity import Entity
from histarchexplorer.models.presentation_view import EntityTypeModel, \
    PresentationView, Relation
from histarchexplorer.utils.view_util import get_cite_button

sidebar_elements = app.config['SIDEBAR_OPTIONS']
valid_routes = {item['route'] for item in sidebar_elements}


def check_p46_geoms(
        id):  # todo replace this check with API. Benchmark for 50505 local postgres (1 row retrieved starting from 1 in 1 s 443 ms (execution: 1 s 147 ms, fetching: 296 ms)
    sql = """
          WITH RECURSIVE
              p46_links AS (SELECT *
                            FROM model.link
                            WHERE property_code = 'P46'
                              AND (%(id)s = domain_id OR %(id)s = range_id)

                            UNION

                            SELECT l.*
                            FROM model.link l
                                     JOIN p46_links pl
                                          ON l.property_code = 'P46'
                                              AND (l.domain_id = pl.range_id OR l.range_id = pl.domain_id)),
              all_ids AS (SELECT domain_id AS id
                          FROM p46_links
                          UNION
                          SELECT range_id AS id
                          FROM p46_links
                          UNION
                          SELECT %(id)s AS id)
          SELECT EXISTS (SELECT 1
                         FROM model.entity e
                                  JOIN all_ids a ON e.id = a.id
                                  JOIN model.link gl ON e.id = gl.domain_id
                             AND gl.property_code = 'P53'
                                  JOIN model.gis g ON gl.range_id = g.entity_id
                         LIMIT 1) AS has_row; \
          """
    # Execute parameterized query
    g.cursor.execute(sql, {'id': id})
    result = g.cursor.fetchone()
    return result[0] if result else False


def get_root_id(
        id):  # todo alternative with api: Benchmarl for 77841: 1 row retrieved starting from 1 in 122 ms (execution: 80 ms, fetching: 42 ms)
    sql = """
          WITH RECURSIVE parent_chain AS (
              -- Anchor: start with the link where 77841 is the range_id
              SELECT domain_id,
                     range_id,
                     0 AS level
              FROM model.link
              WHERE property_code = 'P46'
                AND range_id = %(id)s

              UNION ALL

              -- Recursive part: find the parent link where the current domain_id is the new row's range_id
              SELECT l.domain_id,
                     l.range_id,
                     pc.level + 1 AS level
              FROM model.link l
                       JOIN parent_chain pc
                            ON l.property_code = 'P46'
                                AND l.range_id = pc.domain_id)
          SELECT domain_id
          FROM parent_chain
          ORDER BY level DESC
          LIMIT 1; \
          """
    # Execute parameterized query
    g.cursor.execute(sql, {'id': id})
    result = g.cursor.fetchone()
    return result[0] if result else id


def get_root_type(id):
    sql = """
            WITH RECURSIVE parent_chain AS (
            SELECT
                domain_id,
                range_id,
                0 AS level
            FROM model.link
            WHERE property_code = 'P127'
              AND domain_id =  %(id)s
        
            UNION
        
            SELECT
                 %(id)s AS domain_id,
                 %(id)s AS range_id,
                0 AS level
        
            WHERE NOT EXISTS (
                SELECT 1 FROM model.link
                WHERE property_code = 'P127'
                  AND domain_id =  %(id)s
            )
        
            UNION ALL
        
            SELECT l.domain_id,
                   l.range_id,
                   pc.level + 1 AS level
            FROM model.link l
            JOIN parent_chain pc ON l.property_code = 'P127' AND l.domain_id = pc.range_id
        )
        
        SELECT range_id
        FROM parent_chain
        ORDER BY level DESC
        LIMIT 1;
        """

    g.cursor.execute(sql, {'id': id})
    result = g.cursor.fetchone()
    return result[0] if result else id


def check_geom(id):
    """Checks if an ID has geometry in model.gis via a linked entity."""
    sql = """SELECT EXISTS (SELECT 1
                            FROM model.gis
                            WHERE entity_id = (SELECT range_id
                                               FROM model.link
                                               WHERE domain_id = %(id)s
                                                 AND property_code = 'P53'
                                               LIMIT 1)); \
          """
    g.cursor.execute(sql, {'id': id})
    result = g.cursor.fetchone()
    #print(id if result and result[0] else None)

    return id if result and result[0] else None


def get_first_geom(id):
    """Recursively finds the first entity with geometry."""
    id_to_return = check_geom(id)
    if id_to_return:
        return id_to_return

    # Try to find the parent entity (domain_id)
    sql = """SELECT domain_id
             FROM model.link
             WHERE range_id = %(id)s
               AND property_code = 'P46'
             LIMIT 1; \
          """
    g.cursor.execute(sql, {'id': id})
    result = g.cursor.fetchone()

    if result:
        parent_id = result[0]
        return get_first_geom(parent_id)  # Recursively check the parent
    return None  # No parent found with geometry


@app.route('/entity/<int:id_>')
@app.route('/entity/<int:id_>/<tab_name>')
def entity(id_: int, tab_name="overview") -> str:
    if tab_name not in valid_routes:
        abort(404)
    return render_template(
        'entity.html',
        sidebar_elements=[
            {**item, 'order': 0} if item['route'] == tab_name else item
            for item in sidebar_elements],
        page_name="landing",
        active_tab=tab_name,
        entity_id=id_)



@app.route('/get_entity/<int:id_>/<tab_name>')
def get_entity(id_: int, tab_name=None) -> str:
    related_entities = {}
    catalogue_entities = []
    categorized_types = None

    main_image = None
    initial_images = []
    remaining_images = []
    more_images = False
    number_of_images = 0
    ancestor_entities = []
    feature = None
    hierarchy = None



    main_entity = PresentationView.from_api(id_)
    data = {'entity': main_entity.to_json()}
    categorized_types = get_categorized_types(main_entity)
    hierarchy = {
        'subs': get_sub_count(main_entity),
        'root': get_hierarchy(main_entity)}
    match tab_name:
        case 'feature':
            # todo: core information about the feature are available in the main entity
            feature = Entity.get_entity(id_, Parser())
        # todo: test if really needed
        #case 'features':
        #    features = Entity.get_entity(
        #        id_, Parser(
        #            show=['when', 'types', 'names', 'depictions', 'description', 'relations']
        #        )
        #    )

        case 'map':
            map_data = get_map_data(id_)
            # todo: rewrite get_map_data
            #   can bring the geometries on map, but they are not filled and clickable
            map_data_= {'type': 'FeatureCollection', 'features': []}
            first_geom = None
            tmp_root = hierarchy['root'].copy()
            tmp_root.reverse()
            for entry in tmp_root:
                if entry.geometries and entry.system_class != 'place':
                    first_geom = entry.geometries[0]
                    break
            for k in ['place', 'feature', 'stratigraphic_unit', 'artifact', 'human_remains']:
                for item in main_entity.relations.get(k, []):
                    if item.geometries:
                        # right now only the first geometry is taken, refactor for multiple
                        geometry = item.geometries[0].to_dict()
                        geometry['properties']['id'] = item.id
                        geometry['properties']['label'] = item.name
                        geometry['properties']['class'] = item.system_class
                        if first_geom.geometry.id == item.id:
                            geometry['properties']['main'] = True
                        geometry['geometry']['shapeType'] = geometry['properties']['shapeType']
                        map_data_['features'].append(geometry)
            if not map_data['features']:
                abort(404)
            data['spatial'] = map_data

        case 'catalogue':
            c_entities = Entity.get_linked_entities_by_properties_recursive(
                id_,
                get_parser_for_landing(id_))
            if main_entity.system_class != 'place':
                catalogue_entities = []
            else:
                catalogue_entities = build_entity_tree(c_entities)
                for entity_ in catalogue_entities:
                    entity.all_child_depictions = collect_child_depictions(entity_)

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
            remaining_images = images[2:]
            more_images = len(remaining_images) > 0
            number_of_images = len(images+[main_image])

        case 'media':
            pass

        case _ if tab_name not in ['feature']:
            print('Invalid tab name provided. Aborting with 404.')
            abort(404)


    return render_template(
        f'tabs/{tab_name}.html',
        data=json.dumps(data),
        entity=main_entity,
        categorized_types=categorized_types,
        features=feature,
        main_image=main_image,
        initial_images=initial_images,
        remaining_images=remaining_images,
        more_images=more_images,
        total_images=number_of_images,
        manifests=[img.iiif_manifest for img in main_entity.files],
        related_entities=related_entities or {},
        cite_button=get_cite_button(main_entity),
        catalogue_entities=catalogue_entities,
        ancestor_entities=ancestor_entities,
        hierarchy=hierarchy)


def get_map_data(id_):

    geom_there = check_p46_geoms(id_)
    if geom_there:
        first_geom = get_first_geom(id_)
        id_to_fetch = get_root_id(id_)
        entities = Entity.get_linked_entities_by_properties_recursive(
            id_to_fetch, Parser(show=['geometry'], properties=['P46']))
        features = {'type': 'FeatureCollection', 'features': []}
        for ent in entities:
            property = {'id': ent.id, 'label': ent.name, 'class': ent.system_class}
            if ent.id == first_geom and ent.system_class != 'Place':
                property['main'] = True
            if ent.system_class in ['Feature', 'Place', 'Stratigraphic unit', 'Human remains',
                                    'Artifact'] and ent.geometry:
                features['features'].append({
                    'type': 'Feature',
                    'geometry': ent.geometry,
                    'properties': property,
                })
        return features
    return {'type': 'FeatureCollection', 'features': []}


def get_parser_for_landing(id_: int) -> Parser:
    simple_entity = Entity.get_entity(id_, Parser())
    match simple_entity.system_class.capitalize():
        case 'Place' | 'Feature' | 'Stratigraphic unit':
            properties = ['P46', 'P67']
        case 'Human remains' | 'Artifact':
            properties = ['P46', 'P67', 'P52']
        case 'Source' | 'Source translation':
            properties = ['P67', 'P73', 'P128']
        case 'Event' | 'Acquisition' | 'Activity' | 'Creation' | 'Move' | \
             'Production' | 'Modification':
            properties = [
                'P67', 'P11', 'P14', 'P22', 'P23', 'P25', 'P7',
                'P26', 'P27', 'P24', 'P31', 'P25', 'P108', 'P9',
                'P134']
        case 'Bibliography' | 'Edition' | 'External reference':
            properties = ['P67']
        case 'Group' | 'Person':
            properties = [
                'OA7', 'OA8', 'OA9', 'P107', 'P74', 'P52', 'P11',
                'P14', 'P22', 'P23', 'P25']
        case _:
            properties = []
    return Parser(
        properties=properties,
        limit=0,
        format='lpx',
        centroid='true')


def get_categorized_types(main_entity: PresentationView) -> dict[str, list[EntityTypeModel]]:
    divisions = defaultdict(list)
    for type_ in main_entity.types:
        divisions[type_.division['label'].replace(' ', '_')].append({
            'type': type_, 'icon': type_.division['icon']})
    sorted_divisions = dict(sorted(
        divisions.items(),
        key=lambda x: (x[0] == x[0] == 'case_study', 'other', x[0])
    ))
    return sorted_divisions

def collect_child_depictions(entity_: Entity) -> list[Depiction]:
    all_depictions = []

    def recurse(e: Entity):
        if not hasattr(e, 'children'):
            e.children = []
        for child in e.children:
            all_depictions.extend(child.depictions or [])
            recurse(child)

    if hasattr(entity, 'children'):
        recurse(entity_)
    return all_depictions


def build_entity_tree(entities: list[Entity]) -> list[Entity]:
    entity_dict = {e.id: e for e in entities}

    for entity_ in entities:
        if (entity_.parent
                and 'P46' in entity_.parent.relation_type
                and entity_.parent.relation_to_id in entity_dict):
            parent_entity = entity_dict[entity_.parent.relation_to_id]
            if not hasattr(parent_entity, 'children'):
                parent_entity.children = []
            parent_entity.children.append(entity_)

    tree = []
    for entity_ in entities:
        if entity_.parent and entity_.parent.relation_to_id in entity_dict:
            continue
        if hasattr(entity_, 'children'):
            tree.extend(entity_.children)
    return tree



def get_hierarchy(main_entity: PresentationView) -> list[Relation | None]:
    root = []
    match main_entity.system_class:
        case 'feature':
            root.append(main_entity.relations['place'][0])
        case 'stratigraphic_unit':
            for feature in main_entity.relations.get('feature', []):
                for relation in feature.relation_types:
                    if relation['relationTo'] == main_entity.id:
                        root.append(feature)
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
            root.append(main_entity.relations['place'][0])
    root.reverse()
    return root


def get_sub_count(main_entity: PresentationView) -> int:
    count = 0
    sub_relations_map = {
        'place': ['feature', 'stratigraphic_unit', 'artifact', 'human_remains'],
        'feature': ['stratigraphic_unit', 'artifact', 'human_remains'],
        'stratigraphic_unit': ['artifact', 'human_remains'],
        'artifact': ['artifact', 'human_remains']}
    for rel_type in sub_relations_map.get(main_entity.system_class, []):
        count += len(main_entity.relations.get(rel_type, []))
    return  count
