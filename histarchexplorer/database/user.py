from typing import Any

from flask import g

SQL = """
    SELECT 
        u.id,
        u.username,
        u.password,
        u.active,
        u.real_name,
        u.info,
        u.created,
        u.modified,
        u.email, 
        r.name as group_name
    FROM web."user" u
    LEFT JOIN web.group r ON u.group_id = r.id """


def get_user_by_id(user_id: int) -> dict[str, Any]:
    g.openatlas_cursor.execute(f'{SQL} WHERE u.id = %(id)s;', {'id': user_id})
    return g.openatlas_cursor.fetchone()

def get_by_username(username: str) -> dict[str, Any]:
    g.openatlas_cursor.execute(
        f'{SQL} WHERE LOWER(u.username) = LOWER(%(username)s);',
        {'username': username})
    return g.openatlas_cursor.fetchone()
