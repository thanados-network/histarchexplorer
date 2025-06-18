from typing import Any

from flask import g


def get_config_properties() -> Any:
    g.cursor.execute('''
        SELECT id, name, domain, range, 'direct' AS direction  FROM 
        tng.config_properties
        UNION ALL
        SELECT id, name_inv, range,domain, 'inverse' AS direction FROM 
        tng.config_properties''')
    return g.cursor.fetchall()


def set_hidden_entities(entities ):
    pass
