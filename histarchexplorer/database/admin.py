import json
import os
from typing import Any, NamedTuple

from flask import abort, g, current_app
import bleach

ALLOWED_HTML_TAGS = [
    'b', 'strong', 'i', 'em', 'u',
    'a',
    'ul', 'ol', 'li',
    'p', 'br',
    'span',
    'img']

ALLOWED_HTML_ATTRIBUTES = {
    'a': ['href', 'title', 'target', 'rel'],
    'img': ['src', 'alt']}

ALLOWED_HTML_PROTOCOLS = ['http', 'https', 'mailto']


def sanitize_richtext(html: str) -> str:
    """Sanitize user-provided HTML for rich text fields."""
    return bleach.clean(
        html,
        tags=ALLOWED_HTML_TAGS,
        attributes=ALLOWED_HTML_ATTRIBUTES,
        protocols=ALLOWED_HTML_PROTOCOLS,
        strip=True)


def get_config_links() -> Any:
    g.cursor.execute(
        """
        SELECT l.id        AS link_id,
               l.sortorder AS sortorder,
               s.id        AS start_id,
               s.name      AS start_name,
               cp.name     AS config_property,
               cp.id       AS property_id,
               'direct'    AS direction,
               e.name      AS end_name,
               e.id        AS end_id,
               r.name      AS role,
               r.id        AS role_id
        FROM tng.links l
                 JOIN tng.entities s ON l.domain_id = s.id
                 JOIN tng.entities e ON l.range_id = e.id
                 JOIN tng.properties cp ON l.property = cp.id
                 LEFT JOIN tng.entities r ON l.attribute = r.id
        UNION ALL
        SELECT l.id        AS link_id,
               l.sortorder AS sortorder,
               s.id        AS start_id,
               s.name      AS start_name,
               cp.name_inv AS config_property,
               cp.id       AS property_id,
               'inverse'   AS direction,
               e.name      AS end_name,
               e.id        AS end_id,
               r.name      AS role,
               r.id        AS role_id
        FROM tng.links l
                 JOIN tng.entities s ON l.range_id = s.id
                 JOIN tng.entities e ON l.domain_id = e.id
                 JOIN tng.properties cp ON l.property = cp.id
                 LEFT JOIN tng.entities r ON l.attribute = r.id
        ORDER BY sortorder
        """)
    return g.cursor.fetchall()


def get_config_properties() -> Any:
    g.cursor.execute(
        '''
        SELECT id, name, domain_type_id, range_type_id, 'direct' AS direction
        FROM tng.properties
        UNION ALL
        SELECT id,
               name_inv,
               range_type_id,
               domain_type_id,
               'inverse' AS direction
        FROM tng.properties''')
    return g.cursor.fetchall()


def get_config_class_by_id(id_: int) -> int | None:
    g.cursor.execute(
        'SELECT class_id FROM tng.entities WHERE id = %s',
        (id_,))
    return (g.cursor.fetchone() or {}).get('class_id')


def add_new_map(data: dict[str, str]) -> int:
    g.cursor.execute(
        '''
        INSERT INTO tng.maps
            (name, display_name, sortorder, tilestring)
        VALUES (%(name)s, %(display_name)s, %(sort_order)s, %(tile_string)s)
        RETURNING id
        ''', {
            'name': data.get('name'),
            'display_name': data.get('display_name'),
            'sort_order': data.get('sort_order'),
            'tile_string': data.get('tile_string')})

    row = g.cursor.fetchone()
    return row['id'] if row else 0


def delete_map(map_id: int) -> None:
    g.cursor.execute(
        'DELETE FROM tng.maps WHERE id = %(map_id)s',
        {'map_id': map_id})


def update_map(data: dict[str, str]) -> None:
    g.cursor.execute(
        """
        UPDATE tng.maps
        SET name         = NULLIF(%(name)s, ''),
            display_name = NULLIF(%(display_name)s, ''),
            sortorder    = CASE
                               WHEN %(sortorder)s = '' THEN NULL
                               ELSE CAST(%(sortorder)s AS integer)
                END,
            tilestring   = NULLIF(%(tilestring)s, '')
        WHERE id = %(map_id)s
        """,
        data)


def check_if_main_project_exist() -> bool:
    g.cursor.execute(
        "SELECT 1 FROM tng.entities WHERE class_id = 5 LIMIT 1")
    return g.cursor.fetchone() is not None


def delete_entry(id_: int) -> None:
    g.cursor.execute(
        'DELETE FROM tng.entities WHERE id = %(id)s',
        {'id': id_})


def add_entry(data: dict[str, str | int]) -> int:
    config_class = g.config_classes_map.get(data['category'])
    if config_class is None:
        raise ValueError(f"Unknown category {data['category']}")
    if config_class == 5 and check_if_main_project_exist():
        abort(404)
    g.cursor.execute(
        """
        INSERT INTO tng.entities
        (email, website, orcid_id, image, case_study_type_id, class_id,
         acronym, license_id)
        VALUES (NULLIF(%(email)s, ''),
                NULLIF(%(website)s, ''),
                NULLIF(%(orcid_id)s, ''),
                NULLIF(%(image)s, ''),
                NULLIF(%(case_study)s, NULL),
                %(class_id)s,
                %(acronym)s,
                %(license_id)s)
        RETURNING id
        """, {
            'email': data.get('email'),
            'website': data.get('website'),
            'orcid_id': data.get('orcid_id'),
            'image': data.get('image'),
            'case_study': data.get('case_study'),
            'acronym': data.get('acronym'),
            'class_id': config_class,
            'license_id': data.get('license_id')})

    id_ = g.cursor.fetchone()['id']
    _upsert_jsonb_fields(id_, data)

    return id_


def update_config_entry(data: dict[str, str | int]) -> None:
    config_id = data['config_id']
    if not check_if_config_entry_exist(int(config_id)):
        abort(404)
    g.cursor.execute(
        """
        UPDATE tng.entities
        SET email              = NULLIF(%(email)s, ''),
            website            = NULLIF(%(website)s, ''),
            orcid_id           = NULLIF(%(orcid_id)s, ''),
            image              = NULLIF(%(image)s, ''),
            case_study_type_id = %(case_study)s,
            acronym            = %(acronym)s,
            license_id         = %(license_id)s
        WHERE id = %(config_id)s
        """,
        data)
    _upsert_jsonb_fields(int(config_id), data)


def _upsert_jsonb_fields(config_id: int, data: dict[str, str | int]) -> None:
    language = g.language
    valid_cols = {'address', 'description', 'name'}
    for col in valid_cols:
        val = data.get(col, '')
        if col in ('description') and val:
            val = sanitize_richtext(str(val))
        if val:
            g.cursor.execute(
                f"""
                UPDATE tng.entities
                   SET {col} = jsonb_set(
                                 COALESCE({col}, '{{}}'),
                                 %(path)s,
                                 %(value)s::jsonb,
                                 true)
                 WHERE id = %(config_id)s
                """, {
                    'path': [language],
                    'value': json.dumps(val),
                    'config_id': config_id})
        else:
            g.cursor.execute(
                f"""
                UPDATE tng.entities
                   SET {col} = COALESCE({col}, '{{}}') - %(key)s
                 WHERE id = %(config_id)s
                """, {
                    'key': language,
                    'config_id': config_id})


def update_sort_order(table: str, params: list[dict[str, int]]) -> None:
    g.cursor.executemany(
        f"UPDATE tng.{table} SET sortorder = %(order)s WHERE id = %(id)s",
        params)


def check_sortorder() -> int:
    g.cursor.execute(
        '''
        SELECT COALESCE(MAX(sortorder) + 1, 1) AS next_order
        FROM tng.links
        WHERE sortorder IS NOT NULL''')
    return g.cursor.fetchone()['next_order']


def get_openatlas_entity(id_: int) -> dict[str, Any]:
    g.openatlas_cursor.execute(
        '''
        SELECT id, name, openatlas_class_name
        FROM model.entity
        WHERE id = %(id)s''', {'id': id_})
    return g.openatlas_cursor.fetchone()


def add_link(data: dict[str, Any]) -> None:
    g.cursor.execute(
        '''
        INSERT INTO tng.links
        (domain_id, range_id, property, attribute, sortorder)
        VALUES (%(domain)s, %(range)s, %(prop)s, NULLIF(%(attribute)s, 0),
                %(sortorder)s)
        ''', {
            'domain': data['domain'],
            'range': data['range'],
            'prop': data['prop'],
            'attribute': data['role'],
            'sortorder': data['sortorder']})


def delete_link(id_: int) -> None:
    g.cursor.execute(
        """
        DELETE
        FROM tng.links
        WHERE id = %(link_id)s
        """, {
            'link_id': id_})


def check_if_config_entry_exist(id_: int) -> bool:
    g.cursor.execute(
        'SELECT 1 FROM tng.entities WHERE id = %(id)s',
        {'id': id_})
    return g.cursor.fetchone() is not None


def get_licenses() -> Any:
    g.cursor.execute('SELECT * FROM tng.licenses ORDER BY category, label')
    return g.cursor.fetchall()


def get_file_licenses() -> dict[str, Any]:
    g.cursor.execute('''
        SELECT f.filename, fl.license_id, fl.attribution 
        FROM tng.file_licenses fl
        JOIN tng.files f ON fl.file_id = f.id
    ''')
    return {row['filename']: {'license_id': row['license_id'], 'attribution': row['attribution']} for row in g.cursor.fetchall()}


def add_license(spdx_id: str, uri: str, label: str, category: str) -> None:
    g.cursor.execute(
        """
        INSERT INTO tng.licenses (spdx_id, uri, label, category)
        VALUES (%(spdx_id)s, %(uri)s, %(label)s, %(category)s)
        ON CONFLICT (spdx_id) DO NOTHING
        """,
        {'spdx_id': spdx_id, 'uri': uri, 'label': label, 'category': category}
    )


def delete_license(license_id: int) -> None:
    g.cursor.execute('DELETE FROM tng.licenses WHERE id = %(id)s', {'id': license_id})


def update_file_license(filename: str, license_id: int, attribution: str) -> None:
    # First get file_id from filename
    g.cursor.execute('SELECT id FROM tng.files WHERE filename = %s', (filename,))
    res = g.cursor.fetchone()
    if not res:
        return # Or handle error
    file_id = res['id']

    g.cursor.execute(
        """
        INSERT INTO tng.file_licenses (file_id, license_id, attribution)
        VALUES (%(file_id)s, %(license_id)s, %(attribution)s)
        ON CONFLICT (file_id) DO UPDATE SET license_id = %(license_id)s, attribution = %(attribution)s
        """,
        {'file_id': file_id, 'license_id': license_id, 'attribution': attribution}
    )


def get_all_files_from_db(file_type: str) -> list[dict[str, Any]]:
    g.cursor.execute('SELECT id, filename, is_default FROM tng.files WHERE type = %s AND is_active = TRUE ORDER BY filename', (file_type,))
    return [{'id': row['id'], 'filename': row['filename'], 'is_default': row['is_default']} for row in g.cursor.fetchall()]


def get_files_by_type_from_db(file_type: str) -> list[dict[str, Any]]:
    return get_all_files_from_db(file_type)


def add_file_to_db(filename: str, file_type: str, is_default: bool = False) -> None:
    g.cursor.execute(
        'SELECT id FROM tng.files WHERE filename = %(filename)s AND type = %(type)s',
        {'filename': filename, 'type': file_type})
    row = g.cursor.fetchone()
    if row:
        g.cursor.execute(
            'UPDATE tng.files SET is_active = TRUE, is_default = %(is_default)s WHERE id = %(id)s',
            {'id': row['id'], 'is_default': is_default})
    else:
        g.cursor.execute(
            'INSERT INTO tng.files (type, filename, is_default, is_active) VALUES (%(type)s, %(filename)s, %(is_default)s, TRUE)',
            {'type': file_type, 'filename': filename, 'is_default': is_default})


def delete_file_from_db(filename: str, file_type: str) -> None:
    g.cursor.execute(
        'SELECT is_default FROM tng.files WHERE filename = %(filename)s AND type = %(type)s',
        {'filename': filename, 'type': file_type})
    row = g.cursor.fetchone()
    if row and row['is_default']:
        g.cursor.execute(
            'UPDATE tng.files SET is_active = FALSE WHERE filename = %(filename)s AND type = %(type)s',
            {'filename': filename, 'type': file_type})
    else:
        g.cursor.execute(
            'DELETE FROM tng.files WHERE filename = %(filename)s AND type = %(type)s',
            {'filename': filename, 'type': file_type})


def rename_file_in_db(old_name: str, new_name: str, file_type: str) -> None:
    g.cursor.execute(
        'UPDATE tng.files SET filename = %(new_name)s WHERE filename = %(old_name)s AND type = %(type)s',
        {'old_name': old_name, 'new_name': new_name, 'type': file_type})


def synchronize_files_with_db(file_type: str, folder_path: str, is_default_source: bool) -> None:
    if not os.path.exists(folder_path):
        return

    fs_files = set()
    for f in os.listdir(folder_path):
        if not f.startswith('.'):  # Ignore dotfiles like .gitignore
            fs_files.add(f)

    # Get all active filenames of this type from DB
    g.cursor.execute('SELECT filename FROM tng.files WHERE type = %s', (file_type,))
    db_filenames = {row['filename'] for row in g.cursor.fetchall()}

    # Add new files from filesystem to DB if they don't exist yet
    for filename in fs_files:
        add_file_to_db(filename, file_type, is_default=is_default_source)


# Wrapper functions for Logos
def get_all_logos_from_db() -> list[dict[str, Any]]:
    return get_all_files_from_db('logo')


def add_logo_to_db(filename: str, is_default: bool = False) -> None:
    add_file_to_db(filename, 'logo', is_default)


def delete_logo_from_db(filename: str) -> None:
    delete_file_from_db(filename, 'logo')


def rename_logo_in_db(old_name: str, new_name: str) -> None:
    rename_file_in_db(old_name, new_name, 'logo')


def synchronize_logos_with_db() -> None:
    logo_path = os.path.join(current_app.static_folder, 'images', 'logos')
    synchronize_files_with_db('logo', logo_path, is_default_source=True)


# Wrapper functions for Assets
def get_all_assets_from_db() -> list[dict[str, Any]]:
    return get_all_files_from_db('asset')


def add_asset_to_db(filename: str, is_default: bool = False) -> None:
    add_file_to_db(filename, 'asset', is_default)


def delete_asset_from_db(filename: str) -> None:
    delete_file_from_db(filename, 'asset')


def rename_asset_in_db(old_name: str, new_name: str) -> None:
    rename_file_in_db(old_name, new_name, 'asset')


def synchronize_assets_with_db() -> None:
    asset_path = os.path.join(current_app.static_folder, 'assets')
    synchronize_files_with_db('asset', asset_path, is_default_source=True)


# Wrapper functions for Teams
def get_all_teams_from_db() -> list[dict[str, Any]]:
    return get_all_files_from_db('team')


def add_team_to_db(filename: str, is_default: bool = False) -> None:
    add_file_to_db(filename, 'team', is_default)


def delete_team_from_db(filename: str) -> None:
    delete_file_from_db(filename, 'team')


def rename_team_in_db(old_name: str, new_name: str) -> None:
    rename_file_in_db(old_name, new_name, 'team')


def synchronize_teams_with_db() -> None:
    file_type = 'team'
    static_team_path = os.path.join(current_app.static_folder, 'images', 'team')
    uploaded_team_path = os.path.join(current_app.root_path, '..', 'uploads', 'team')

    # First, add new files from static source to DB
    synchronize_files_with_db(file_type, static_team_path, is_default_source=True)

    # Then, add new files from uploaded source to DB
    synchronize_files_with_db(file_type, uploaded_team_path, is_default_source=False)

    # Now, get all files from both filesystem sources
    all_fs_files = set()
    for path in [static_team_path, uploaded_team_path]:
        if os.path.exists(path):
            for f in os.listdir(path):
                if not f.startswith('.'):  # Ignore dotfiles
                    all_fs_files.add(f)

    # Get all active files from DB for this file_type
    g.cursor.execute('SELECT id, filename FROM tng.files WHERE type = %s AND is_active = TRUE', (file_type,))
    db_records = {row['filename']: row['id'] for row in g.cursor.fetchall()}

    # Deactivate files in DB that no longer exist in *any* filesystem source
    for filename, file_id in db_records.items():
        if filename not in all_fs_files:
            g.cursor.execute(
                'UPDATE tng.files SET is_active = FALSE WHERE id = %s',
                (file_id,)
            )


def synchronize_icons_with_db() -> None:
    file_type = 'icon'
    static_icon_path = os.path.join(current_app.static_folder, 'images', 'icons')
    uploaded_icon_path = os.path.join(current_app.root_path, '..', 'uploads', 'icons')

    synchronize_files_with_db(file_type, static_icon_path, is_default_source=True)
    synchronize_files_with_db(file_type, uploaded_icon_path, is_default_source=False)

    all_fs_files = set()
    for path in [static_icon_path, uploaded_icon_path]:
        if os.path.exists(path):
            for f in os.listdir(path):
                if not f.startswith('.'):
                    all_fs_files.add(f)

    g.cursor.execute('SELECT id, filename FROM tng.files WHERE type = %s AND is_active = TRUE', (file_type,))
    db_records = {row['filename']: row['id'] for row in g.cursor.fetchall()}

    for filename, file_id in db_records.items():
        if filename not in all_fs_files:
            g.cursor.execute(
                'UPDATE tng.files SET is_active = FALSE WHERE id = %s',
                (file_id,)
            )
