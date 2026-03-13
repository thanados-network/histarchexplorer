import re
import os
from datetime import datetime
from typing import Any, Optional

from flask import g, url_for, current_app


def split_date_string(date_str: Optional[str]) -> str:
    if not date_str:
        return ""
    date_part = date_str.split("T")[0]
    if date_part.startswith("-"):  # handle BC years manually
        sign, date_part = "-", date_part[1:]
        year, month, day = date_part.split("-")
        return (f"{sign}{day.zfill(2)}.{month.zfill(2)}."
                f"{year.lstrip('0') or '0'}")
    try:
        return datetime.fromisoformat(date_str).strftime("%d.%m.%Y")
    except ValueError:  # pragma: no cover
        return date_part  # fallback for malformed date strings


def is_full_year_span(date_from: str, date_to: str) -> bool:
    return date_from.startswith("01.01.") and date_to.startswith("31.12.")


def format_date(date_from: str, date_to: str) -> str:
    bc_from = date_from.startswith("-")
    bc_to = date_to.startswith("-")

    # Remove '-' for formatting display
    clean_from = date_from.lstrip("-")
    clean_to = date_to.lstrip("-")

    def year_part(date_: str) -> str:
        return date_.split(".")[2].lstrip("0") if "." in date_ else date_

    if date_from and date_to:
        if is_full_year_span(date_from, date_to) or date_from == date_to:
            year = year_part(clean_from)
            era = "BC" if bc_from else "AD"
            return f"{year} {era}"
        return (f"{year_part(clean_from)} {'BC' if bc_from else 'AD'} "
                f"- {year_part(clean_to)} {'BC' if bc_to else 'AD'}")

    # Only one side available
    date = ".".join(s.lstrip("0") for s in
                    clean_from.split(".")) if date_from else clean_to
    return f"{date} {'BC' if bc_from else ''}".strip()


def get_render_type(mime_type: str) -> str:
    match mime_type:
        case None:
            render_type = 'unknown'
        case "model/gltf-binary" | "model/glb" | "model/gltf+json":
            render_type = '3d_model'
        case "image/webp":
            render_type = 'webp'
        case "application/pdf":
            render_type = 'pdf'
        case 'image/svg+xml':
            render_type = 'svg'
        case _ if mime_type.startswith("video/"):
            render_type = 'video'
        case _ if mime_type.startswith("image/"):
            render_type = 'image'
        case _:
            render_type = 'unknown'
    return render_type


def get_icon_url(filename: str) -> str:
    uploads_path = os.path.join(current_app.root_path, '..', 'uploads', 'icons')
    if os.path.exists(os.path.join(uploads_path, filename)):
        return url_for('uploaded_icon', filename=filename)
    return url_for('static', filename=f'images/icons/{filename}')


def get_divisions(
        id_: int,
        type_hierarchy: list[dict[str, str]]) -> dict[str, str]:
    type_ids_to_check = {id_} | {
        int(t['identifier'].rsplit('/', 1)[-1]) for t in type_hierarchy}

    for label, data in g.type_divisions.items():
        configured_ids = set(data.get('ids', []))
        if not type_ids_to_check.isdisjoint(configured_ids):
            icon_type = data.get('icon_type')
            icon_value = data.get('icon_value')

            if icon_type == 'icon' and icon_value:
                return {
                    'label': label,
                    'icon_url': get_icon_url(icon_value)
                }
            elif icon_type == 'bootstrap' and icon_value:
                return {
                    'label': label,
                    'icon': f'<i class="bi {icon_value}"></i>'
                }
            return {
                'label': label,
                'icon': '<i class="bi bi-box"></i>'
            }

    return {'label': 'other', 'icon': '<i class="bi bi-boxes"></i>'}


def get_description_translated(description: str) -> None | dict[str, str]:
    if not description:
        return None

    matches = re.findall(r'##(\w+)_##(.*?)##_\1##', description, re.DOTALL)
    if matches:
        lang_dict = {lang: text.strip() for lang, text in matches}
        if 'de' not in lang_dict and 'en' in lang_dict:
            lang_dict['de'] = lang_dict['en']

        return lang_dict
    parts = description.split('##German')
    if len(parts) > 1:
        return {
            'en': parts[0].strip(),
            'de': parts[1].strip()}

    fallback_text = description.strip()
    return {'en': fallback_text, 'de': fallback_text}


def to_camel_case(snake_str: str) -> str:
    """Convert snake_case string to camelCase."""
    components = snake_str.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


def dict_to_camel_case(data: Any) -> Any:
    """Recursively transform dictionary keys to camelCase."""
    if isinstance(data, list):
        return [dict_to_camel_case(i) for i in data]
    if isinstance(data, dict):
        return {
            to_camel_case(k): dict_to_camel_case(v)
            for k, v in data.items()}
    return data
