import requests
from typing import Any, Optional


def fetch_doi_metadata(doi: str) -> Optional[dict[str, Any]]:
    """
    Fetch metadata from Crossref for a given DOI.
    """
    if not doi:
        return None

    # Remove 'doi:' prefix if present
    if doi.lower().startswith('doi:'):
        doi = doi[4:]

    # Clean the DOI string (remove whitespace)
    doi = doi.strip()

    url = f"https://api.crossref.org/works/{doi}"
    try:
        response = requests.get(
            url, timeout=10, headers={
                'User-Agent': 'Histarchexplorer/0.4.0 (https://github.com/openatlas/histarchexplorer; mailto:info@openatlas.eu)'})
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
            # Try different date fields
            published = data.get('published-print') or \
                        data.get('published-online') or \
                        data.get('created')
            if published:
                date_parts = published.get('date-parts', [[None]])[0]
                if date_parts[0]:
                    year = date_parts[0]

            return {
                'title': title,
                'authors': authors,
                'year': year,
                'doi': doi,
                'url': data.get('URL', f"https://doi.org/{doi}")
            }
    except Exception:
        pass

    return None
