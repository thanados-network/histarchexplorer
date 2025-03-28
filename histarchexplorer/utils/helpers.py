from typing import Any

from flask import request, session
from histarchexplorer import app


def get_translation(item: dict[str, str]) -> dict[str, str]:
    language = session.get(
        'language',
        request.accept_languages.best_match(
            app.config['LANGUAGES'].keys()))

    preferred_lan = app.config['PREFERRED_LANGUAGE']
    if item:
        for key in item:
            if key == language:
                return {'language': key, 'label': item[key]}
        for key in item:
            if key == preferred_lan:
                return {'language': key, 'label': item[key]}
        return {'language': next(iter(item)), 'label': item[next(iter(item))]}
    return {'language': '', 'label': ''}


def to_serializable(obj: Any) -> Any:
    if isinstance(obj, list):
        return [to_serializable(item) for item in obj]
    elif hasattr(obj, "__dict__"):
        return {
            key: to_serializable(value) for key, value in obj.__dict__.items()}
    elif isinstance(obj, dict):
        return {key: to_serializable(value) for key, value in obj.items()}
    else:
        return obj
