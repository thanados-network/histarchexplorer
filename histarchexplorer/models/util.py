from typing import Optional


def uc_first(string: str) -> str:
    return str(string)[0].upper() + str(string)[1:] if string else ''


def split_date_string(data: Optional[str]) -> Optional[str]:
    return '.'.join(map(str, data.split('T')[0].split('-')[::-1])) \
        if data else ''


def format_date(
        date_from: Optional[str],
        date_to: Optional[str]) -> Optional[str]:
    return f'between {date_from} and {date_to}' if date_to else date_from
