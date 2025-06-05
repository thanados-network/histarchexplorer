import json
from flask import render_template
from histarchexplorer import app
from histarchexplorer.database.about import *
from histarchexplorer.models.about import build_object, build_connections
from histarchexplorer.utils import helpers


@app.route('/about')
def about() -> str:


    # Example usage
    #print(json.dumps(build_object(build_connections, 1), ensure_ascii=False, indent=4))

    g.cursor.execute(about_str_sql)

    project_result = g.cursor.fetchone()
    project = {
        'name': (helpers.get_translation(project_result[0]))['label'],
        'description': (helpers.get_translation(project_result[1]))['label'],
        'legal_notice': (helpers.get_translation(project_result[2]))['label'],
        'imprint': (helpers.get_translation(project_result[3]))['label']
    }


    institutions_result = get_institutions()


    institutions = []
    for row in institutions_result:
        institutions.append({
            'name': (helpers.get_translation(row[0]))['label'],
            'address': (helpers.get_translation(row[1]))['label'] if row[1] else " ",
            'website': row[2],
            'role': (helpers.get_translation(row[4]))['label'] if row[4] else "No role",
            'image': row[3]
        })



    persons_result = get_persons()


    persons = {}
    for row in persons_result:
        person_name = (helpers.get_translation(row[0]))['label']

        if person_name not in persons:
            persons[person_name] = {
                'name': (helpers.get_translation(row[0]))['label'],
                'roles': [] ,
                'image': row[1],
                'affiliation': (helpers.get_translation(row[3]))['label'],
                'website': row[4],
                'email': row[5]
            }
        persons[person_name]['roles'].append((helpers.get_translation(row[2]))['label'])

    persons_list = list(persons.values())

    return render_template(
        'about.html',
        project=project,
        institutions=institutions,
        persons=persons_list)
