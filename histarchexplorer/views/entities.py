from flask import render_template, g

from histarchexplorer import app

from histarchexplorer.utils import cerberos

@app.route('/entities')
def entities() -> str:
    g.cursor.execute('''
        SELECT openatlas_class_name, COUNT(*) as count
        FROM model.entity
        GROUP BY openatlas_class_name
        ORDER BY count DESC
    ''')

    entities = g.cursor.fetchall()
    # list of tuples to dictionary (entities_dict); keys = entities; values = associated IDs.
    entities_dict = {entity[0]: entity[1] for entity in entities}

    view_classes = cerberos.gatekeeper()
    print(view_classes)


    g.cursor.execute('''
            SELECT shown_entities from tng.settings LIMIT 1''')
    shown_entities = (g.cursor.fetchone()).shown_entities

    for shown_entity in shown_entities:
        print(shown_entity)

    cerberos.gatekeeper()

    return render_template('entities.html', entities=entities_dict, view_classes=view_classes, viewcount=len(view_classes.keys()))


