from typing import Optional

import requests
from flask import Response, render_template, request, url_for

from histarchexplorer import app


# todo: delete old view if done with overview files
@app.route('/iiif_viewer')
def view_mirador() -> str:
    urls_param = request.args.get('urls')  # comma-separated string
    url_list = urls_param.split(',') if urls_param else []

    print(f'url_list: {url_list}')
    return render_template('media/iiif.html', manifests=url_list)


@app.route('/view/<string:render_type>/<int:id_>')
@app.route('/view/<string:render_type>/<int:id_>/<int:origin_id>')
def view_media(render_type: str, id_: int, origin_id: Optional[int] = None):
    """
    Generic media viewer for all render types.
    """
    back_url = None
    if origin_id:
        back_url = url_for('entity_view', tab_name='media', id_=origin_id)
    # IIIF don't use manifest url, but get it per API call or existing data
    match render_type:
        case 'image':
            template = render_template(
                'media/iiif.html',
                manifest=request.args.get('manifest'),
                back_url=back_url)
        case '3d_model':
            template = render_template(
                'media/3d_model.html',
                file_id=id_,
                file_url=f"{app.config['API_URL']}display/{id_}",
                back_url=back_url)
        case 'video':
            template = render_template(
                'media/video.html',
                file_id=id_,
                file_url=f"{app.config['API_URL']}display/{id_}",
                back_url=back_url)
        case 'pdf':
            return render_template(
                "media/pdf.html",
                file_id=id_,
                file_url=f"{app.config['API_URL']}display/{id_}",
                back_url=back_url)
        case 'svg':
            return render_template(
                "media/svg.html",
                file_id=id_,
                file_url=f"{app.config['API_URL']}display/{id_}",
                back_url=back_url)
        case _:
            template = f"Unsupported render type: {render_type}", 400

    return template

# "video": {color: "#118ab2", icon: "bi-play-btn-fill"},
# "pdf": {color: "#ef476f", icon: "bi-filetype-pdf"},
# "svg": {color: "#ffd166", icon: "bi-vector-pen"},
# "unknown": {color: "#adb5bd", icon: "bi-question-circle"}
