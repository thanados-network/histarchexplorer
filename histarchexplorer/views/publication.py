from flask import request
from histarchexplorer import app
from histarchexplorer.database.publications import (
    get_publications, get_all_projects)
from histarchexplorer.utils.view_util import (
    render_page_template, get_publication_citation)


@app.route('/publications')
def publications() -> str:
    all_publications = get_publications()

    selected_project = request.args.get('project', type=int)
    selected_type = request.args.get('type')
    selected_year = request.args.get('year', type=int)
    search_query = request.args.get('q', '').lower()

    filtered_publications = []
    for pub in all_publications:
        if selected_project:
            if not any(
                    ent['id'] == selected_project for ent in pub['entities']):
                continue
        if selected_type and pub['publication_type'] != selected_type:
            continue
        if selected_year and pub['year'] != selected_year:
            continue
        if search_query:
            if (search_query not in pub['title'].lower() and
                    (pub['authors'] and
                     search_query not in pub['authors'].lower())):
                continue
        pub['citation'] = get_publication_citation(pub)
        filtered_publications.append(pub)

    # Get unique years and types for filters
    years = sorted(list(
        {pub['year'] for pub in all_publications if pub['year']}),
        reverse=True)
    types = sorted(list(
        {pub['publication_type'] for pub in all_publications if
         pub['publication_type']}))
    projects = get_all_projects()

    return render_page_template(
        'publications',
        publications=filtered_publications,
        years=years,
        types=types,
        projects=projects,
        selected_project=selected_project,
        selected_type=selected_type,
        selected_year=selected_year,
        search_query=search_query)
