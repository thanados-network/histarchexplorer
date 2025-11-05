from flask import render_template, request

from histarchexplorer import app


@app.route('/view/<string:render_type>/<int:id_>')
def view_media(render_type: str, id_: int):
    """
    Generic media viewer for all render types.
    """
    match render_type:
        case 'image':
            template = render_template('viewer/iiif.html', file_id=id_)
        case '3d_model':
            template = render_template('viewer/3d_model.html', file_id=id_)
        case 'video':
            template = render_template('viewer/video.html', file_id=id_)
        case 'pdf':
            return render_template("viewer/pdf.html", file_id=id_)
        case 'svg':
            return render_template("viewer/svg.html", file_id=id_)
        case _:
            template = f"Unsupported render type: {render_type}", 400

    return template


# todo: remove when overview is done
@app.route('/iiif_viewer')
def view_mirador() -> str:
    urls_param = request.args.get('urls')  # comma-separated string
    url_list = urls_param.split(',') if urls_param else []

    print(f'url_list: {url_list}')
    return (render_template
            ('iiif.html',
             manifests=url_list))
