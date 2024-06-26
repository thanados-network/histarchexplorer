from flask import render_template, g
from histarchexplorer import app
from typing import Dict, Any, Tuple


def capitalize_first(value: str) -> str:
    if not value:
        return ''
    return value[0].upper() + value[1:]


app.jinja_env.filters['capitalize_first'] = capitalize_first


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
        SELECT c.name, c.address, c.website, role.name AS role
        FROM tng.links l
        JOIN tng.config c ON l.range_id = c.id
        LEFT JOIN tng.config role ON l.attribute = role.id AND role.config_class = '3' --role name & config class
        WHERE l.domain_id = (SELECT id FROM tng.config WHERE config_class = '5') -- only links concerning main-project
        AND c.config_class = '4'
    """

    g.cursor.execute(institutions_sql)
    institutions_result = g.cursor.fetchall()

    institutions = []
    for row in institutions_result:
        institutions.append({
            'name': row[0],
            'address': row[1],
            'website': row[2],
            'role': row[3] if row[3] else "No role"  # Do we need this?
        })

    persons_sql = """
SELECT p.name, p.image, COALESCE(b.name, '') AS role
FROM tng.links l
JOIN tng.config p ON l.range_id = p.id
JOIN tng.config_properties cp ON l.property = cp.id
LEFT JOIN tng.config b ON l.attribute = b.id AND b.config_class = '3'
WHERE l.domain_id = (SELECT id FROM tng.config WHERE config_class = '5')
AND p.config_class = '2'
AND cp.id = 4;
    """

    g.cursor.execute(persons_sql)
    persons_result = g.cursor.fetchall()

    persons = {}
    for row in persons_result:
        person_name = row[0]
        print(row[0])
        if person_name not in persons:
            persons[person_name] = {
                'name': row[0],
                'roles': [],
                'image': row[1]
            }
        persons[person_name]['roles'].append(row[2])

    persons_list = list(persons.values())

    for person in persons_list:
        print(f"Person: {person['name']}, Roles: {person['roles']}")

    # Sort the persons_list - main coordinator and principal investigator first
    def prioritize_roles(person: Dict[str, Any]) -> Tuple[int, str]:
        roles_priority = {"main coordinator": 0, "principal investigator": 1}
        priority = min((roles_priority.get(role.lower(), 99) for role in person['roles']), default=99)
        return (priority, person['name'].lower())

    persons_list.sort(key=prioritize_roles)

    for person in persons_list:
        print(f"Sorted Person: {person['name']}, Roles: {person['roles']}")

    return render_template('about.html', project=project, institutions=institutions, persons=persons_list)
