from typing import Optional


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
