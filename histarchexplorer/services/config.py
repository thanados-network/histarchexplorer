from histarchexplorer.database.config_types import get_config_types_sql


def get_config_types() -> dict[str, int]:
    data = {}
    for config_type in get_config_types_sql():
        data[config_type.name] = config_type.id
    return data

