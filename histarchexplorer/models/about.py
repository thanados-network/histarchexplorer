from flask import g

from histarchexplorer.database.about import build_connections_sql, \
    get_models_sql


def build_object(build_connections, id):

    g.cursor.execute(get_models_sql, (id,))
    object_data = g.cursor.fetchone()
    if not object_data:
        return {}

    object = {}
    column_names = [description[0] for description in g.cursor.description]
    for column_name, column_value in zip(column_names, object_data):
        if column_value:
            object[column_name] = column_value

    # Integrate connections
    object['connections'] = build_connections(object['id'])['properties']
    return object


def build_connections(id):
    g.cursor.execute(build_connections_sql, (id,))
    rows = g.cursor.fetchall()

    result = {'properties': []}
    property_map = {}

    for row in rows:
        property_id = row[1]
        if property_id not in property_map:
            property_obj = {'id': property_id, 'name': row[0], 'targets': []}
            property_map[property_id] = property_obj
            result['properties'].append(property_obj)

    for row in rows:
        property_id = row[1]
        target_id = row[5]
        target_obj = build_object(build_connections, target_id)
        if target_obj and target_obj not in property_map[property_id]['targets']:
            property_map[property_id]['targets'].append(target_obj)

        role = row[3]
        if role and 'roles' not in target_obj:
            target_obj['roles'] = []
        if role and role not in target_obj['roles']:
            target_obj['roles'].append(role)

    return result
