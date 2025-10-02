from typing import Any

from flask import g

from histarchexplorer.api.api_access import ApiAccess
from histarchexplorer.api.parser import Parser


def get_entities_count_by_case_study() -> dict[str, Any]:
    parser = Parser(type_id=[
        config.case_study for config
        in g.config_entities if config.case_study])
    return ApiAccess.get_system_class_count(parser)
