from flask import g


def get_config_entities() -> tuple[str]:
    g.cursor.execute(
        f"""SELECT 
            c.id,
            c.name,
            c.description,
            c.website,
            c.legal_notice,
            c.imprint,
            c.type,
            c.address, 
            c.email,
            c.image,      
            c.orcid_id,
            cc.name as type_name 
        FROM 
            tng.entities as c
		JOIN  tng.types as cc ON c.type = cc.id;""")
    return g.cursor.fetchall()


def get_project_attributes_sql(
        id_: int,
        config_type_id: int) -> tuple[str]:
    g.cursor.execute(
        """
        SELECT l.domain_id,
               attribute.name AS attribute
        FROM tng.links l
                 JOIN tng.entities c ON l.range_id = c.id
                 LEFT JOIN tng.entities attribute ON l.attribute = attribute.id
            AND attribute.type = %(attribute_id)s
        WHERE l.range_id = %(id)s
          AND c.type = %(config_type_id)s
        ORDER BY l.sortorder, l.id;
        """, {
            'id': id_,
            'config_type_id': config_type_id,
            'attribute_id': g.config_types['attribute']})
    return g.cursor.fetchall()


def get_affiliations(id_: int) -> tuple[str]:
    g.cursor.execute(
        """
        SELECT DISTINCT l.range_id,
                        a.name    AS affiliation,
                        attribute.name AS attribute
        FROM tng.links l
                 LEFT JOIN tng.entities attribute
                           ON l.attribute = attribute.id
                               AND attribute.type = %(attribute_id)s
                 LEFT JOIN tng.links la
                           ON la.range_id = l.range_id
                               AND la.property = %(affiliation_id)s
                 LEFT JOIN tng.entities a
                           ON la.range_id = a.id
        WHERE l.domain_id = %(id)s;
        """, {
            'id': id_,
            'affiliation_id': 2,
            'attribute_id': g.config_types['attribute']})
    return g.cursor.fetchall()
