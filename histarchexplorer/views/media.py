from flask import request, render_template

from histarchexplorer import app


@app.route('/iiif_viewer')
def view_mirador() -> str:
    urls_param = request.args.get('urls')  # comma-separated string
    url_list = urls_param.split(',') if urls_param else []

    print(f'url_list: {url_list}')
    return render_template('iiif.html',manifests=url_list)
