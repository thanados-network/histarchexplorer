from typing import Any, List, Optional
from flask import g


def get_publications() -> List[dict[str, Any]]:
    sql = """
        SELECT p.*, f.filename
        FROM tng.publications p
        LEFT JOIN tng.files f ON p.file_id = f.id
        ORDER BY p.year DESC, p.title ASC
    """
    g.cursor.execute(sql)
    publications = g.cursor.fetchall()

    for pub in publications:
        pub['entities'] = get_linked_entities(pub['id'])

    return publications


def get_publication_by_id(pub_id: int) -> Optional[dict[str, Any]]:
    sql = """
        SELECT p.*, f.filename
        FROM tng.publications p
        LEFT JOIN tng.files f ON p.file_id = f.id
        WHERE p.id = %(id)s
    """
    g.cursor.execute(sql, {'id': pub_id})
    pub = g.cursor.fetchone()
    if pub:
        pub['entities'] = get_linked_entities(pub['id'])
    return pub


def add_publication(data: dict[str, Any]) -> int:
    sql = """
        INSERT INTO tng.publications (title, authors, year, publication_type, 
                                     doi, url, file_id)
        VALUES (%(title)s, %(authors)s, %(year)s, %(publication_type)s, 
                %(doi)s, %(url)s, %(file_id)s)
        RETURNING id
    """
    g.cursor.execute(sql, {
        'title': data.get('title'),
        'authors': data.get('authors'),
        'year': data.get('year') or None,
        'publication_type': data.get('publication_type'),
        'doi': data.get('doi'),
        'url': data.get('url'),
        'file_id': data.get('file_id') or None})
    pub_id = g.cursor.fetchone()['id']
    return pub_id


def update_publication(pub_id: int, data: dict[str, Any]) -> None:
    sql = """
        UPDATE tng.publications
        SET title = %(title)s,
            authors = %(authors)s,
            year = %(year)s,
            publication_type = %(publication_type)s,
            doi = %(doi)s,
            url = %(url)s,
            file_id = %(file_id)s
        WHERE id = %(id)s
    """
    g.cursor.execute(sql, {
        'title': data.get('title'),
        'authors': data.get('authors'),
        'year': data.get('year') or None,
        'publication_type': data.get('publication_type'),
        'doi': data.get('doi'),
        'url': data.get('url'),
        'file_id': data.get('file_id') or None,
        'id': pub_id})


def delete_publication(pub_id: int) -> None:
    g.cursor.execute("DELETE FROM tng.publications WHERE id = %s", (pub_id,))


def link_publication_to_entities(pub_id: int, entity_ids: List[int]) -> None:
    # First, delete existing links
    g.cursor.execute(
        "DELETE FROM tng.publication_entities WHERE publication_id = %s",
        (pub_id,))

    # Then insert new ones
    if entity_ids:
        params = [{'pub_id': pub_id, 'ent_id': ent_id} for ent_id in entity_ids]
        g.cursor.executemany(
            """INSERT INTO tng.publication_entities (publication_id, entity_id) 
               VALUES (%(pub_id)s, %(ent_id)s)""",
            params)


def get_linked_entities(pub_id: int) -> List[dict[str, Any]]:
    sql = """
        SELECT e.id, e.name
        FROM tng.entities e
        JOIN tng.publication_entities pe ON e.id = pe.entity_id
        WHERE pe.publication_id = %s
    """
    g.cursor.execute(sql, (pub_id,))
    return g.cursor.fetchall()


def get_all_projects() -> List[dict[str, Any]]:
    sql = """
        SELECT e.id, e.name
        FROM tng.entities e
        JOIN tng.classes c ON e.class_id = c.id
        WHERE c.name IN ('project', 'main-project')
        ORDER BY e.name->>'en'
    """
    g.cursor.execute(sql)
    return g.cursor.fetchall()
