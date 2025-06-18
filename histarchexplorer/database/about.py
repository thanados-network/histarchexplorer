from flask import g


def get_projects() -> tuple[str]:
    g.cursor.execute(
        f"""SELECT 
            c.id,
            c.name,
            c.description,
            c.website,
            c.legal_notice,
            c.imprint,
            c.config_class,
            cc.name as class_name
        FROM 
            tng.config as c
		JOIN  tng.config_classes as cc ON c.config_class = cc.id 
		WHERE cc.id IN ({g.config_classes['project']}, {g.config_classes['main-project']});""")
    return g.cursor.fetchall()

def get_institutions() -> tuple[str]:
    g.cursor.execute(
        f"""SELECT 
            id,
            name,
            description,
            address, 
            email,
            website,
            image
        FROM 
            tng.config
        WHERE 
            config_class = {g.config_classes['institution']};""")
    return g.cursor.fetchall()

def get_persons() -> tuple[str]:
    g.cursor.execute(
        f"""SELECT 
            id,
            name,
            description,
            email,
            image,
            orcid_id
        FROM 
            tng.config
        WHERE 
            config_class = {g.config_classes['person']};""")
    return g.cursor.fetchall()

def get_project_roles_sql(
        id_: int,
        config_class_id: int) -> tuple[str]:
    g.cursor.execute(
        """
        SELECT l.domain_id,
               role.name AS role
        FROM tng.links l
        JOIN tng.config c ON l.range_id = c.id
            LEFT JOIN tng.config role ON l.attribute = role.id
            AND role.config_class = %(role_id)s
        WHERE l.range_id = %(id)s
            AND c.config_class = %(config_class_id)s
        ORDER BY l.sortorder, l.id;
        """, {
            'id': id_,
            'config_class_id': config_class_id,
            'role_id': g.config_classes['role']})
    return g.cursor.fetchall()

def get_affiliations(id_: int) -> tuple[str]:
    g.cursor.execute(
        """
        SELECT DISTINCT
            l.range_id,
            a.name AS affiliation,
            role.name AS role
        FROM tng.links l
        LEFT JOIN tng.config role 
            ON l.attribute = role.id 
            AND role.config_class = %(role_id)s
        LEFT JOIN tng.links la 
            ON la.range_id = l.range_id 
            AND la.property = %(affiliation_id)s
        LEFT JOIN tng.config a 
            ON la.range_id = a.id
        WHERE l.domain_id = %(id)s;
        """, {
            'id': id_,
            'affiliation_id': 2,
            'role_id': g.config_classes['role']})
    return g.cursor.fetchall()
