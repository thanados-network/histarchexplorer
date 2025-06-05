from flask import g


def get_institutions():
    institutions_sql = """
        SELECT 
            c.name,
            c.address, 
            c.website,
            c.image, 
            role.name AS role
        FROM tng.links l
        JOIN tng.config c ON l.range_id = c.id
        LEFT JOIN tng.config role ON l.attribute = role.id AND role.config_class = '3' --role name & config class
        WHERE 
            l.domain_id = (SELECT id FROM tng.config WHERE config_class = '5') -- only links concerning main-project
        AND c.config_class = '4'
        ORDER BY l.sortorder, l.id;
    """
    g.cursor.execute(institutions_sql)
    return g.cursor.fetchall()

def get_persons():
    persons_sql = """
        SELECT 
            p.name, 
            p.image, 
            b.name AS role, 
            a.name AS affiliation, 
            COALESCE(a.website, '') AS website, 
            COALESCE(p.email, '') AS email
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
    return g.cursor.fetchall()

build_connections_sql = '''
    SELECT p.name AS property, p.id AS property_id, c.name AS target, d.name AS role, l.sortorder, c.id AS target_id
    FROM tng.links l
    JOIN tng.config c ON l.range_id = c.id
    JOIN tng.config_properties p ON l.property = p.id
    LEFT JOIN tng.config d ON l.attribute = d.id
    WHERE domain_id = %s
    ORDER BY property, sortorder
'''

get_models_sql = 'SELECT * FROM tng.config WHERE id = %s'

about_str_sql = "SELECT name, description, legal_notice, imprint FROM tng.config WHERE id = 1"