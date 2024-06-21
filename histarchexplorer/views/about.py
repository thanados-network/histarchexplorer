from flask import render_template, g
from histarchexplorer import app


@app.route('/about')
def about() -> str:
    project_sql = """
        SELECT name, description, legal_notice, imprint
        FROM tng.config
        WHERE config_class = '5'
    """

    g.cursor.execute(project_sql)
    project_result = g.cursor.fetchone()

    project = {
        'name': project_result[0],
        'description': project_result[1],
        'legal_notice': project_result[2],
        'imprint': project_result[3]
    }

    institutions_sql = """
        SELECT c.name, c.description
        FROM tng.links l
        JOIN tng.config c ON l.range_id = c.id
        WHERE l.domain_id = (SELECT id FROM tng.config WHERE config_class = '5')
        AND c.config_class = '4'
    """

    g.cursor.execute(institutions_sql)
    institutions_result = g.cursor.fetchall()

    institutions = []
    for row in institutions_result:
        institutions.append({
            'name': row[0],
            'description': row[1]
        })

        persons_sql = """
               SELECT p.name, r.name AS role
               FROM tng.links l
               JOIN tng.config p ON l.range_id = p.id
               JOIN tng.config_properties cp ON l.property = cp.id
               JOIN tng.config r ON l.attribute = r.id
               WHERE l.domain_id = (SELECT id FROM tng.config WHERE config_class = '5')
               AND p.config_class = '2'
               AND cp.id = 4  -- Assuming 'has core member' property ID is 4
               AND r.config_class = '3'  -- Roles are in tng.config with config_class = '3'
           """

        g.cursor.execute(persons_sql)
        persons_result = g.cursor.fetchall()

        persons = []
        for row in persons_result:
            persons.append({
                'name': row[0],
                'role': row[1]
            })

    return render_template('about.html', project=project, institutions=institutions, persons=persons)
