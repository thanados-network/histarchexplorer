import requests
from flask import Response, request, render_template

from histarchexplorer import app


@app.route('/iiif_viewer')
def view_mirador() -> str:
    urls_param = request.args.get('urls')  # comma-separated string
    url_list = urls_param.split(',') if urls_param else []

    print(f'url_list: {url_list}')
    return render_template('iiif.html',manifests=url_list)


@app.route('/render-pdf/<int:id_>')
def render_pdf(id_: int):
    pdf_url = f"{app.config['API_URL']}display/{id_}"
    response = requests.get(pdf_url, stream=True)

    if response.status_code != 200:
        return f"Failed to fetch PDF (status {response.status_code})", 502

    return Response(
        response.iter_content(chunk_size=4096),
        content_type="application/pdf",
        headers={"Content-Disposition": "inline; filename=document.pdf"})
