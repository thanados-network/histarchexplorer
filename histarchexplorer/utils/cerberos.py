from flask import g
from histarchexplorer import app
def gatekeeper ():

    g.cursor.execute('''
               SELECT shown_entities from tng.settings LIMIT 1''')
    shown_entities = (g.cursor.fetchone()).shown_entities

    g.cursor.execute('''
        SELECT openatlas_class_name, COUNT(*) as count
        FROM model.entity
        WHERE openatlas_class_name = ANY(%(shown_entities)s)
        GROUP BY openatlas_class_name
        ORDER BY count DESC
    ''', {'shown_entities': shown_entities})

    entities = g.cursor.fetchall()
    print(entities)

    return_classes = {}
    view_classes = app.config['VIEW_CLASSES']
    for view_class in view_classes:
        for record in entities:
            if record.openatlas_class_name in view_classes[view_class]:
                if view_class not in return_classes:
                    return_classes[view_class] ={'count':0, 'subunits': []}
                return_classes[view_class]['subunits'].append({record.openatlas_class_name: record.count})
                return_classes[view_class]['count'] += record.count

    return return_classes
