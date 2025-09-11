
import json
from collections import defaultdict
from typing import Any

from flask import abort, g, render_template

from histarchexplorer import app, cache
from histarchexplorer.api.parser import Parser
from histarchexplorer.database.entity import get_entity_by_id
from histarchexplorer.models.depiction import Depiction
from histarchexplorer.models.entity import Entity
from histarchexplorer.models.types import Types
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
    data = {}
    main_entity = None
    related_entities = {}
    catalogue_entities = []

    # entities = Entity.get_linked_entities_by_properties_recursive(
    #     id_,
    #     get_parser_for_getentity(id_)
    # )
    # main_entity = get_main_entity(id_, entities)


    def get_map_data():
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


    features = []
    main_image = None
    initial_images = []
    remaining_images = []
    more_images = False
    number_of_images = 0
    all_images = []
    # related_entities_json = json.dumps({}, ensure_ascii=False, indent=4)



    if tab_name == 'feature':
        entities = Entity.get_linked_entities_by_properties_recursive(
            id_, Parser(
                show=['when', 'types', 'names', 'depictions', 'description', 'relations'],
                properties=['P46'],
                relation_type=['P46'],
                column='id',
                sort='asc',
                search=[str({
                    "entitySystemClass": [{
                        "logicalOperator": "and",
                        "operator": "notEqual",
                        "values": ["place"]}]})]
            )
        )
        features = entities

    elif tab_name == 'features':
        features = Entity.get_entity(
            id_, Parser(
                show=['when', 'types', 'names', 'depictions', 'description', 'relations']
            )
        )

    elif tab_name == 'map':
        map_data = get_map_data()
        if not map_data['features']:
            #print('No spatial features found. Aborting with 404.')
            abort(404)
        data['spatial'] = map_data
    elif tab_name == 'catalogue':

        c_entities = Entity.get_linked_entities_by_properties_recursive(
            id_,
            get_parser_for_landing(id_))
        catalogue_entities = build_entity_tree(c_entities)
        for entity in catalogue_entities:
            entity.all_child_depictions = collect_child_depictions(entity)

    elif tab_name == 'overview':
        # data = get_entity()
        entities = Entity.get_linked_entities_by_properties_recursive(
            id_,
            get_parser_for_landing(id_))
        main_entity= get_main_entity(id_, entities)

        if isinstance(main_entity.geometry, dict) and main_entity.geometry.get("type") == "GeometryCollection":
            main_entity.geometry["geometries"] = [
                geom for geom in main_entity.geometry.get("geometries", [])
                if geom.get("type") == "Point"
            ]

        #print(main_entity.geometry)
        #print('=== DEBUG PERSON ENTITY ===')
        #print('ID:', main_entity.id)
        #print('Name:', main_entity.name)
        #print('Class:', main_entity.system_class)
        #print('Formated date:', main_entity.formated_date)
        #print('Types (Chronology):', [(t.label, t.root) for t in main_entity.types if t.root == 'Chronology'])

        related_entities = get_related_entities(main_entity, entities)

        data = {
            'entity': json.dumps(
                main_entity.to_serializable(),
                ensure_ascii=False,
                indent=4),
            'categorized_types': json.dumps(
                categorized_types(main_entity),
                ensure_ascii=False,
                indent=4)
        }

        images = []

        # related_entities_json = json.dumps(related_entities, ensure_ascii=False, indent=4)

        for image in main_entity.depictions:
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


    #Media-tab

    elif tab_name == 'media':
        entities = Entity.get_linked_entities_by_properties_recursive(
            id_,
            get_parser_for_landing(id_)
        )
        main_entity = get_main_entity(id_, entities)

        all_images = main_entity.depictions

        data = {
            'entity': json.dumps(main_entity.to_serializable(), ensure_ascii=False),
            'categorized_types': json.dumps(categorized_types(main_entity), ensure_ascii=False)
        }

    elif tab_name not in valid_routes:
        if tab_name not in ['feature']:
            print('Invalid tab name provided. Aborting with 404.')
            abort(404)
    #print(all_images)
    #print([img.iiif_manifest for img in all_images])

    return render_template(
        f'tabs/{tab_name}.html',
        data=json.dumps(data),
        entity=main_entity,
        categorized_types=categorized_types(main_entity) if main_entity else None,
        features=features,
        main_image=main_image,
        initial_images=initial_images,
        remaining_images=remaining_images,
        more_images=more_images,
        total_images=number_of_images,
        all_images=all_images,
        manifests=[img.iiif_manifest for img in all_images],
        related_entities=related_entities or {},
        cite_button=get_cite_button(main_entity),
        catalogue_entities=catalogue_entities )

    # related_entities=related_entities_json)

def collect_child_depictions(entity: Entity) -> list[Depiction]:
    all_depictions = []

    def recurse(e: Entity):
        if not hasattr(e, 'children'):
            e.children = []
        for child in e.children:
            all_depictions.extend(child.depictions or [])
            recurse(child)

    if hasattr(entity, 'children'):
        recurse(entity)
    return all_depictions

def build_entity_tree(entities: list[Entity]) -> list[Entity]:
    entity_dict = {e.id: e for e in entities}

    for entity in entities:
        if entity.parent and entity.parent.relation_to_id in entity_dict:
            parent_entity = entity_dict[entity.parent.relation_to_id]
            if not hasattr(parent_entity, 'children'):
                parent_entity.children = []
            parent_entity.children.append(entity)

    tree = []
    for entity in entities:
        if entity.parent and entity.parent.relation_to_id in entity_dict:
            continue
        if hasattr(entity, 'children'):
            tree.extend(entity.children)
    return tree

def get_parser_for_landing(id_: int) -> Parser:
    simple_entity = get_entity_by_id(id_)
    match simple_entity.openatlas_class_name.capitalize():
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



def get_main_entity(id_: int, entities: list[Entity]) -> Entity:
    for entity in entities:
        if entity.id == id_:
            return entity
    raise ValueError(f"Entity with id {id_} not found.")


def get_ancestor_entities(main_entity: Entity, entities: list[Entity]) -> list[dict]:
    ancestor_entities = []
    current_entity = main_entity

    while current_entity:
        # If there is a parent, get the actual entity it points to
        if current_entity.parent:
            parent_entity = next(
                (entity for entity in entities if entity.id == current_entity.parent.relation_to_id),
                None
            )
            if parent_entity:
                ancestor_entities.append({
                    'id': parent_entity.id,
                    'name': parent_entity.name,
                    'system_class': parent_entity.system_class
                })
                current_entity = parent_entity  # Move up to the next level
            else:
                break  # Exit if no parent entity
        else:
            break
    ancestor_entities.reverse()
    return ancestor_entities


def get_related_entities(
        main_entity: Entity,
        entities: list[Entity]) -> dict[str, dict[str, list[Entity]]]:
    related_entities: dict[str, Any] = defaultdict(lambda: defaultdict(list))
    for subunit in entities:
        if subunit.id == main_entity.id:
            continue
        match subunit.system_class:
            case 'Group' | 'Person':
                related_entities[subunit.system_class][subunit.name].append(
                    subunit)
            case _:
                if not subunit.types:
                    continue
                for type_ in subunit.types:
                    label = type_.type_hierarchy[0]['label']
                    if label in app.config['STANDARD_TYPES']:
                        related_entities[label][type_.label].append(subunit.to_serializable())
    return related_entities


def categorized_types(main_entity: Entity) -> dict[str, list[Types]]:
    divisions = defaultdict(list)
    for type_ in main_entity.types:
        divisions[type_.division['label'].replace(' ', '_')].append({
            'type': type_.to_serializable(), 'icon': type_.division['icon']})
    sorted_divisions = dict(sorted(
        divisions.items(),
        key=lambda x: (x[0] == x[0] == 'case_study', 'other', x[0])
    ))

    return sorted_divisions

