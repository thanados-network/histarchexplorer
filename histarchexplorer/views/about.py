import json
from flask import render_template, g
from histarchexplorer import app
from histarchexplorer.services.about import Institution, Project
from histarchexplorer.utils import helpers


@app.route('/about')
def about() -> str:

    persons_sql = """
SELECT p.name, p.image, b.name AS role, a.name AS affiliation, COALESCE(a.website, '') AS website, COALESCE(p.email, '') AS email
FROM tng.links l
JOIN tng.config p ON l.range_id = p.id
JOIN tng.config_properties cp ON l.property = cp.id
LEFT JOIN tng.config b ON l.attribute = b.id AND b.config_class = '3'
LEFT JOIN tng.links la ON la.domain_id = p.id AND la.property = 2
LEFT JOIN tng.config a ON la.range_id = a.id
WHERE l.domain_id = (SELECT id FROM tng.config WHERE config_class = '5')
AND p.config_class = '2'
ORDER BY l.sortorder, l.id;
    """

    g.cursor.execute(persons_sql)
    persons_result = g.cursor.fetchall()

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


    project = None
    sub_projects = []
    for p in Project.get_all_localized():
        if p.main_project:
            project = p
            continue
        sub_projects.append(p)

    institutions = []
    for institute in Institution.get_all_localized():
        if roles := institute.roles[project.id_]:
            for role in roles:
                institute.role = role
                institutions.append(institute)


    return render_template(
        'about.html',
        project=project,
        sub_projects=sub_projects,
        institutions=institutions,
        persons=persons_list)
