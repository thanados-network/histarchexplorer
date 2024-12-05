from flask import render_template, g
from histarchexplorer import app
from histarchexplorer.utils import helpers






@app.route('/about')
def about() -> str:

    def build_object(id_: int) -> None:
        g.cursor.execute('SELECT * FROM tng.config WHERE id = %s', (id_,))
        object_data = g.cursor.fetchone()
        object_ = {}
        column_names = [description[0] for description in g.cursor.description]
        for column_name, column_value in zip(column_names, object_data):
            if column_value:
                object_[column_name] = column_value
        #print("build_object:", object_)

    def build_connections(id_: int) -> None:
        g.cursor.execute(
            'SELECT '
            'range_id, '
            'property, '
            'attribute '
            'FROM tng.links '
            'WHERE domain_id = %s', (id_,))
        connections = g.cursor.fetchall()
        #print("build_connections:", connections)

    build_object(1)
    build_connections(1)

    g.cursor.execute('SELECT name, description, legal_notice, imprint FROM tng.config WHERE id = 1')
    project_result = g.cursor.fetchone()

    project = {
        'name': (helpers.get_translation(project_result[0]))['label'],
        'description': (helpers.get_translation(project_result[1]))['label'],
        'legal_notice': (helpers.get_translation(project_result[2]))['label'],
        'imprint': (helpers.get_translation(project_result[3]))['label']
    }

    institutions_sql = """
        SELECT c.name, c.address, c.website, c.image, role.name AS role
        FROM tng.links l
        JOIN tng.config c ON l.range_id = c.id
        LEFT JOIN tng.config role ON l.attribute = role.id AND role.config_class = '3' --role name & config class
        WHERE l.domain_id = (SELECT id FROM tng.config WHERE config_class = '5') -- only links concerning main-project
        AND c.config_class = '4'
        ORDER BY l.sortorder, l.id;
    """

    g.cursor.execute(institutions_sql)
    institutions_result = g.cursor.fetchall()


    institutions = []
    for row in institutions_result:
        institutions.append({
            'name': (helpers.get_translation(row[0]))['label'],
            'address': (helpers.get_translation(row[1]))['label'] if row[1] else " ",
            'website': row[2],
            'role': (helpers.get_translation(row[4]))['label'] if row[4] else "No role",
            'image': row[3]
        })


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
AND cp.id = 4
ORDER BY l.sortorder, l.id;
    """

    g.cursor.execute(persons_sql)
    persons_result = g.cursor.fetchall()
    #print("Persons:", persons_result)

    persons = {}
    for row in persons_result:
        person_name = (helpers.get_translation(row[0]))['label']
        #print(row[0])
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
   # print("Person list:", persons_list)

    return render_template(
        'about.html',
        project=project,
        institutions=institutions,
        persons=persons_list)
