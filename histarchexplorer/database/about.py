from flask import g


def get_config_entities() -> tuple[str]:
    g.cursor.execute(
        f"""SELECT 
            c.id,
            c.name,
            c.acronym,
            c.description,
            c.website,
            c.legal_notice,
            c.imprint,
            c.class_id,
            c.address, 
            c.email,
            c.image,      
            c.orcid_id,
            c.case_study_type_id,
            cc.name as class_name 
        FROM 
            tng.entities as c
        JOIN  tng.classes as cc ON c.class_id = cc.id;""")
    return g.cursor.fetchall()


# def get_project_attributes_sql(
#         id_: int,
#         config_class_id: int) -> tuple[str]:
#     g.cursor.execute(
#         """
#         SELECT l.domain_id,
#                attribute.name AS attribute
#         FROM tng.links l
#                  JOIN tng.entities c ON l.range_id = c.id
#                  LEFT JOIN tng.entities attribute ON l.attribute = attribute.id
#             AND attribute.class_id = %(attribute_id)s
#         WHERE l.range_id = %(id)s
#           AND c.class_id = %(config_class_id)s
#         ORDER BY l.sortorder, l.id;
#         """, {
#             'id': id_,
#             'config_class_id': config_class_id,
#             'attribute_id': g.config_classes['attribute']})
#     return g.cursor.fetchall()

# def get_project_attributes_sql_inverse(
#         id_: int,
#         config_class_id: int) -> tuple[str]:
#     g.cursor.execute(
#         """
#         SELECT l.range_id,
#                attribute.name AS attribute
#         FROM tng.links l
#                  JOIN tng.entities c ON l.domain_id = c.id
#                  LEFT JOIN tng.entities attribute ON l.attribute = attribute.id
#             AND attribute.class_id = %(attribute_id)s
#         WHERE l.domain_id = %(id)s
#           AND c.class_id = %(config_class_id)s
#         ORDER BY l.sortorder, l.id;
#         """, {
#             'id': id_,
#             'config_class_id': config_class_id,
#             'attribute_id': g.config_classes['attribute']})
#     return g.cursor.fetchall()


# def get_affiliations(id_: int) -> tuple[str]:
#     g.cursor.execute(
#         """
#         SELECT DISTINCT l.range_id,
#                         a.name    AS affiliation,
#                         attribute.name AS attribute
#         FROM tng.links l
#                  LEFT JOIN tng.entities attribute
#                            ON l.attribute = attribute.id
#                                AND attribute.class_id = %(attribute_id)s
#                  LEFT JOIN tng.links la
#                            ON la.range_id = l.range_id
#                                AND la.property = %(affiliation_id)s
#                  LEFT JOIN tng.entities a
#                            ON la.range_id = a.id
#         WHERE l.domain_id = %(id)s;
#         """, {
#             'id': id_,
#             'affiliation_id': 2,
#             'attribute_id': g.config_classes['attribute']})
#     return g.cursor.fetchall()
