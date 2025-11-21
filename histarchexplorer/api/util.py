import re
from datetime import datetime
from typing import Optional

from flask import g


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


def format_date(date_from: str, date_to: str) -> Optional[str]:
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
        else:
            return (f"{year_part(clean_from)} {'BC' if bc_from else 'AD'} "
                    f"- {year_part(clean_to)} {'BC' if bc_to else 'AD'}")

    # Only one side available
    date = ".".join(s.lstrip("0") for s in
                    clean_from.split(".")) if date_from else clean_to
    return f"{date} {'BC' if bc_from else ''}".strip()


# def date_template_format(begin: Optional[str], end: Optional[str]) -> str:
#     if begin and end:
#         date = f'{begin} - {end}'
#     elif begin:
#         date = begin
#     elif end:
#         date = end
#     else:
#         date = ''
#     return date


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


def get_icon(id_: int, type_hierarchy: dict[str, str]) -> str:
    icon = g.sidebar_icons.get(int(id_))
    if not icon:
        for type_ in type_hierarchy:
            type_id = int(type_['identifier'].rsplit('/', 1)[-1])
            if g.sidebar_icons.get(type_id):
                icon = g.sidebar_icons.get(type_id)
                break
    return icon or g.sidebar_icons.get('other')


def get_divisions(id_: int, type_hierarchy: dict[str, str]) -> dict[str, str]:
    division = g.type_divisions.get(int(id_))
    if not division:
        for type_ in type_hierarchy:
            type_id = int(type_['identifier'].rsplit('/', 1)[-1])
            if g.type_divisions.get(type_id):
                division = g.type_divisions.get(type_id)
                break
    return (division or
            {'label': 'other', 'icon': '<i class="bi bi-boxes"></i>'})


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
