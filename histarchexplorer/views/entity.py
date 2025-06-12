import json
from collections import defaultdict

from flask import abort, g, render_template

from histarchexplorer import app
from histarchexplorer.api.parser import Parser
from histarchexplorer.models.entity import Entity
from histarchexplorer.models.types import Types

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

def get_recursive_type_ids(id):
    sql = """
            (WITH RECURSIVE children_chain AS (
            -- Anchor: start with the given id as the root
            SELECT
                 %(id)s AS id,   -- your starting ID here
                0 AS level
            UNION ALL
            -- Recursive: find children where the domain_id = parent's id
            SELECT
                l.domain_id AS id,
                cc.level + 1
            FROM model.link l
            JOIN children_chain cc ON l.range_id = cc.id
            WHERE l.property_code = 'P127'
        )
        SELECT id
        FROM children_chain
        ORDER BY level, id)
    """
    g.cursor.execute(sql, {'id': id})
    result = g.cursor.fetchall()
    print('result get_recursive_type_ids(id)')
    print(result)
    return result


def build_id_collection(ids):
    if not ids:
        return []

    result = [
        row[0]
        for id in ids
        for row in get_recursive_type_ids(id)
    ]
    print('result build_id_collection(ids)')
    print(result)
    return result



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
    print(id if result and result[0] else None)

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


def get_browse_list_entities():
    # Fetch filter settings
    g.cursor.execute("""
        SELECT shown_entities, shown_types, hidden_entities, hidden_types, shown_ids, hidden_ids
        FROM tng.settings
        LIMIT 1
    """)
    result = g.cursor.fetchone()

    data = {
        'shown classes': result.shown_entities,
        'hidden classes': result.hidden_entities,
        'shown types': build_id_collection(result.shown_types),
        'hidden types': build_id_collection(result.hidden_types),
        'shown ids': result.shown_ids,
        'hidden ids': result.hidden_ids,
    }




    # Prepare filter values; handle None as empty lists to avoid errors in query
    def parse_json(field):
        if field is None:
            return []
        # Sometimes fields might be stringified JSON
        if isinstance(field, str):
            import json
            return json.loads(field)
        return field

    shown_entities = parse_json(data['shown classes'])
    hidden_entities = parse_json(data['hidden classes'])
    shown_types = parse_json(data['shown types'])
    hidden_types = parse_json(data['hidden types'])
    shown_ids = parse_json(data['shown ids'])
    hidden_ids = parse_json(data['hidden ids'])

    # Build WHERE clauses dynamically
    where_clauses = []
    params = []

    if shown_entities:
        where_clauses.append("e.openatlas_class_name = ANY (%s)")
        params.append(shown_entities)

    if hidden_entities:
        where_clauses.append("e.openatlas_class_name != ALL (%s)")
        params.append(hidden_entities)

    if shown_types:
        where_clauses.append("e.id IN (SELECT a.id FROM model.entity a JOIN model.link b ON a.id = b.domain_id WHERE b.property_code = 'P2' AND b.range_id = ANY (%s))")
        params.append(shown_types)

    if hidden_types:
        where_clauses.append("e.id NOT IN (SELECT a.id FROM model.entity a JOIN model.link b ON a.id = b.domain_id WHERE b.property_code = 'P2' AND b.range_id = ANY (%s))")
        params.append(hidden_types)

    if shown_ids:
        where_clauses.append("e.id = ANY (%s)")
        params.append(shown_ids)

    if hidden_ids:
        where_clauses.append("e.id != ALL (%s)")
        params.append(hidden_ids)

    where_sql = " AND ".join(where_clauses)
    if where_sql:
        where_sql = "WHERE " + where_sql

    query = f"""
        SELECT jsonb_agg(
            jsonb_build_object(
                'id', e.id,
                'name', e.name,
                'description', e.description,
                'class', e.openatlas_class_name,
                'type', e.type,
                'type_id', e.typeid,
                'begin', e.begin,
                'end', e.end
            )
        ) AS items
        FROM (WITH RECURSIVE all_children AS (
    SELECT h.id AS id
    FROM web.hierarchy h
    WHERE h.category = 'standard'

    UNION ALL

    SELECT l.domain_id
    FROM model.link l
    JOIN all_children ac ON l.range_id = ac.id
    WHERE l.property_code = 'P127'
)
SELECT a.name, a.id, a.description, a.openatlas_class_name, ac.id AS typeid, c.name as type, tng.getdates(a.begin_from, a.begin_to, a.begin_comment) AS begin, tng.getdates(a.end_to, a.end_from, a.end_comment) AS end
FROM model.entity a JOIN model.link l1 ON l1.domain_id = a.id
JOIN all_children ac ON l1.range_id = ac.id JOIN model.entity c ON c.id = ac.id WHERE l1.property_code = 'P2' UNION ALL
SELECT a.name, a.id, a.description, a.openatlas_class_name, null AS typeid, null as type, tng.getdates(a.begin_from, a.begin_to, a.begin_comment) AS begin, tng.getdates(a.end_to, a.end_from, a.end_comment) AS end
FROM model.entity a WHERE id NOT IN (SELECT a.id
FROM model.entity a JOIN model.link l1 ON l1.domain_id = a.id
JOIN all_children ac ON l1.range_id = ac.id JOIN model.entity c ON c.id = ac.id WHERE l1.property_code = 'P2')) e {where_sql}
    """

    print((query, tuple(params)))
    g.cursor.execute(query, tuple(params))
    data['entities'] = g.cursor.fetchone()[0] or []

    count_query = f"""
                     SELECT e.openatlas_class_name, COUNT(*) AS count
                     FROM model.entity e
                     {where_sql}
                     GROUP BY e.openatlas_class_name
                     """

    g.cursor.execute(count_query, tuple(params))
    results = g.cursor.fetchall()

    # Load VIEW_CLASSES from app config
    view_classes = app.config.get('VIEW_CLASSES', {})

    # Convert list of (class_name, count) to a dictionary for easy access
    class_count_map = {row[0]: row[1] for row in results}

    # Build categorized counts
    categorized_counts = {}
    for category, class_names in view_classes.items():
        category_counts = [
            {cls: class_count_map[cls]} for cls in class_names if cls in class_count_map
        ]
        if category_counts:  # Only include non-empty categories
            categorized_counts[category] = category_counts

    category_totals = {
        category: sum(next(iter(d.values())) for d in items)
        for category, items in categorized_counts.items()
    }

    data['totals'] = category_totals
    data['counts'] = categorized_counts
    return data



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


@app.route('/entities')
@app.route('/entities/<tab_name>')
def entities(tab_name="") -> str:

    data = get_browse_list_entities()

    filtered_view_classes = {
        key: tuple(list(d.keys())[0] for d in value)
        for key, value in data['counts'].items()
    }

    sidebar_elements = [
        {
            'order': i + 1,
            'route': key,
            'label': f"{key.capitalize()} ({data['totals'][key]})"
        }
        for i, key in enumerate(sorted(data['counts'].keys()))
    ]

    if tab_name == "" and sidebar_elements:
        tab_name = sidebar_elements[0]['route']

    return render_template(
        'entity.html',
        view_classes=filtered_view_classes,
        data=data,
        sidebar_elements=sidebar_elements,
        entity_id=0,
        page_name="landing",
        active_tab=tab_name
    )


@app.route('/get_entities/<tab_name>')
def get_entities(tab_name: str = None) -> str:
    print(tab_name)
    return render_template(
        f'tabs/browse.html',
        tab_name=tab_name)


@app.route('/get_entity/<int:id_>/<tab_name>')
def get_entity(id_: int, tab_name=None) -> str:
    data = {}
    entity_ = None

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

    def serialize_image(image):
        return {
            "url": image.url,
            "title": image.title,
            "iiif_base_path": image.iiif_base_path
        }

    features = []
    main_image = None
    initial_images = []
    more_images = False
    total_images = 0
    # related_entities_json = json.dumps({}, ensure_ascii=False, indent=4)

    # def get_related_entities(
    #         main_entity: Entity,
    #         entities: list[Entity]) -> dict[str, dict[str, list[Entity]]]:
    #     related_entities: dict[str, Any] = defaultdict(lambda: defaultdict(list))
    #     for subunit in entities:
    #         if subunit.id == main_entity.id:
    #             continue
    #         match subunit.system_class:
    #             case 'Group' | 'Person':
    #                 related_entities[subunit.system_class][subunit.name].append(
    #                     subunit)
    #             case _:
    #                 if not subunit.types:
    #                     continue
    #                 for type_ in subunit.types:
    #                     label = type_.type_hierarchy[0]['label']
    #                     if label in app.config['STANDARD_TYPES']:
    #                         related_entities[label][type_.label].append(subunit.to_serializable())
    #     return related_entities

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
            print('No spatial features found. Aborting with 404.')
            abort(404)
        data['spatial'] = map_data

    elif tab_name == 'overview':
        # data = get_entity()
        entity_ = Entity.get_entity(id_, Parser())

        data = {
            'entity': json.dumps(
                entity_.to_serializable(),
                ensure_ascii=False,
                indent=4),
            'categorized_types': json.dumps(
                categorized_types(entity_),
                ensure_ascii=False,
                indent=4)
        }
        # entities = Entity.get_linked_entities_by_properties_recursive(
        #     id_,
        #     get_parser_for_getentity(id_)
        # )
        images = []
        #  related_entities = get_related_entities(main_entity, entities)
        # related_entities_json = json.dumps(related_entities, ensure_ascii=False, indent=4)

        for image in entity_.depictions:
            if image.main_image:
                main_image = serialize_image(image)
            else:
                images.append(serialize_image(image))

        if not main_image and images:
            main_image = images.pop(0)

        initial_images = images[:3]
        more_images = len(images) > 3
        total_images = len(images)

    elif tab_name not in valid_routes:
        if tab_name not in ['feature']:
            print('Invalid tab name provided. Aborting with 404.')
            abort(404)

    return render_template(
        f'tabs/{tab_name}.html',
        data=json.dumps(data),
        entity=entity_,
        categorized_types=categorized_types(entity_) if entity_ else None,
        features=features,
        main_image=main_image,
        initial_images=initial_images,
        more_images=more_images,
        total_images=total_images,
    )
    # related_entities=related_entities_json)


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


def get_parser_for_getentity(id_: int) -> Parser:
    simple_entity = Entity.get_entity(id_, Parser(show=['None']))
    match simple_entity.system_class:
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
        format='lpx')
