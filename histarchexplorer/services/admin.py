import json

from flask import g


def set_hidden_entities(form: list[str]):
    print(form)
    deselected_entities_str = json.dumps(form)
    print(deselected_entities_str)
    g.cursor.execute(
        'UPDATE tng.settings SET hidden_entities = %s',
        (form,)  # This should be a Python list of strings
    )
