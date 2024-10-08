from typing import Any

from histarchexplorer import app
from histarchexplorer.api.api_access import ApiAccess
from histarchexplorer.api.parser import Parser


def get_entities_count_by_case_study() -> dict[str, Any]:
    parser = Parser(type_id=app.config['OPENATLAS_CASE_STUDY_IDS'])
    return ApiAccess.get_system_class_count(parser)
