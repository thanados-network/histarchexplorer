import logging
import re
from typing import Any, Optional
from urllib.parse import quote

import requests  # type: ignore[import-untyped]

logger = logging.getLogger(__name__)
DOI_REGEX = re.compile(r'^10\.\d{4,9}/[-._;()/:A-Za-z0-9]+$')


def fetch_doi_metadata(doi: str) -> Optional[dict[str, Any]]:
    """Fetch metadata from Crossref for a given DOI."""
    if not doi:
        return None

    if doi.lower().startswith('doi:'):
        doi = doi[4:]

    doi = doi.strip()
    if '..' in doi or not DOI_REGEX.match(doi):
        return None

    encoded_doi = quote(doi, safe='/')
    url = f"https://api.crossref.org/works/{encoded_doi}"
    user_agent = (
        'Histarchexplorer/0.4.0 '
        '(https://github.com/openatlas/histarchexplorer; '
        'mailto:info@openatlas.eu)')
    try:
        response = requests.get(
            url, timeout=10, headers={'User-Agent': user_agent})
        if response.status_code == 200:
            data = response.json().get('message', {})

            title = data.get('title', [''])[0]

            authors_list = []
            for author in data.get('author', []):
                given = author.get('given', '')
                family = author.get('family', '')
                if given and family:
                    authors_list.append(f"{family}, {given}")
                elif family:
                    authors_list.append(family)

            authors = '; '.join(authors_list)

            year = None
            published = (
                data.get('published-print')
                or data.get('published-online')
                or data.get('created'))
            if published:
                date_parts = published.get('date-parts', [[None]])[0]
                if date_parts[0]:
                    year = date_parts[0]

            return {
                'title': title,
                'authors': authors,
                'year': year,
                'doi': doi,
                'url': data.get('URL', f"https://doi.org/{encoded_doi}")}
    except Exception as e:
        logger.warning("Failed to fetch DOI metadata for %s: %s", doi, e)

    return None
