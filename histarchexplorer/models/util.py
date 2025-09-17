import re
from typing import Optional

from flask import g


def uc_first(string: str) -> str:
    return str(string)[0].upper() + str(string)[1:] if string else ''


def split_date_string(data: Optional[str]) -> str:
    date = ''
    if data:
        date = '.'.join(map(str, data.split('T')[0].split('-')[::-1]))
    return date


def check_timespan_date(date_from: str, date_to: str) -> bool:
    if '01.01.' in date_from and '31.12.' in date_to:
        return True
    return False


def format_date(
        date_from: str,
        date_to: str) -> Optional[str]:
    # Check if date is BC and remove leading '-'
    bc_date_from = '-' in date_from
    bc_date_to = '-' in date_to
    if bc_date_from:
        date_from.replace('-', '', 1)
    if bc_date_to:
        date_to.replace('-', '', 1)

    date = ''
    if date_from and date_to:
        if check_timespan_date(date_from, date_to) or date_from == date_to:
            date = (date_from.split('.')[2]).lstrip('0')
            date = f"{date} {'BC' if bc_date_from else 'AD'}"
        else:
            from_ = (f"{(date_from.split('.')[2]).lstrip('0')} "
                     f"{'BC' if bc_date_from else 'AD'}")
            to = (f"{(date_to.split('.')[2]).lstrip('0')} "
                  f"{'BC' if bc_date_to else 'AD'}")
            date = f'{from_} - {to}'
    elif date_from or date_to:
        string = [s.lstrip("0") for s in date_from.split('.')]
        date = '.'.join(string)

        date = f"{date} {'BC' if bc_date_from else ''}"
    return date


def date_template_format(begin: Optional[str], end: Optional[str]) -> str:
    if begin and end:
        date = f'{begin} - {end}'
    elif begin:
        date = begin
    elif end:
        date = end
    else:
        date = ''
    return date


def get_render_type(mime_type: str) -> str:
    if mime_type:
        if (mime_type == "model/gltf-binary"
                or mime_type == "model/glb"
                or mime_type == "model/gltf+json"):
            return '3d_model'
        elif mime_type == "image/webp":
            return 'webp'
        elif mime_type == "application/pdf":
            return 'pdf'
        elif mime_type.startswith("image/"):
            return 'image'
    return 'unknown'


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


def get_description_translated(description: str) -> dict[str, str]:
    if description == None:
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
