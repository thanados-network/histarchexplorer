import os
import subprocess
from typing import Optional

from flask import (
    abort, current_app, flash, g, redirect, render_template,
    request, url_for)
from flask_babel import lazy_gettext as _
from flask_login import current_user, login_required
from werkzeug import Response

from histarchexplorer import app
from histarchexplorer.api.helpers import get_entities_count_by_case_study
from histarchexplorer.database.map import check_if_map_id_exist
from histarchexplorer.services.admin import Admin, EntryNotFound
from histarchexplorer.utils.view_util import construct_admin_tabs


@app.route('/admin/')
@app.route('/admin/<tab>')
@app.route('/admin/<tab>/<entry>')
@login_required
def admin(tab: Optional[str] = None, entry: Optional[str] = None) -> str:
    check_manager_user()
    class_items = {
        k: v for k, v in get_entities_count_by_case_study().items()
        if k not in app.config['CLASSES_TO_SKIP']}
    return render_template(
        "admin.html",
        entities=g.config_entities,
        tabs=construct_admin_tabs(),
        activetab=tab,
        activeentry=entry,
        links_data=g.config_links,
        properties=g.config_properties,
        maps=Admin.get_maps(),
        settings=g.settings.get_map_settings(),
        class_items=class_items,
        shown_entities=g.settings.shown_entities,
        hidden_entities=g.settings.hidden_entities,
        view_classes=app.config['VIEW_CLASSES'])


@app.route('/admin/delete_entry/<int:id_>/<tab>')
@login_required
def delete_entry(id_: int, tab: str) -> Response:
    check_manager_user()
    if Admin.get_config_config_classes_by_id(id_) == 5:
        flash(_('Main Project cannot be deleted'), 'danger')
        return redirect(url_for('admin', tab=tab))
    Admin.delete_entry(id_)
    flash('Entry deleted successfully!', 'success')
    return redirect(url_for('admin') + tab)


@app.route('/admin/delete_link/<int:link_id>/<tab>/<entry>')
@login_required
def delete_link(link_id: int, tab: str, entry: str) -> Response:
    check_manager_user()
    Admin.delete_link(link_id)
    flash(_('Link deleted successfully!'), 'success')
    return redirect(url_for('admin', tab=tab, entry=entry))


@app.route('/admin/add_link/', methods=['GET', 'POST'])
@login_required
def add_link() -> Response:
    check_manager_user()
    Admin.add_link({
        'domain': int(request.args.get('domain')),
        'range': int(request.args.get('range')),
        'prop': int(request.args.get('property')),
        'role': int(request.args.get('role')),
        'sortorder': Admin.check_sortorder()})
    flash(_('Link added successfully'), 'success')
    return redirect(
        url_for(
            'admin',
            tab=request.args.get('tab', ''),
            entry=request.args.get('entry', '')))


@app.route('/admin/add_entry', methods=['POST'])
@login_required
def add_entry() -> Response:
    check_manager_user()

    form_data = {
        'category': request.form.get('category', ''),
        'name': request.form.get('name', ''),
        'email': request.form.get('mail', ''),
        'website': request.form.get('website', ''),
        'orcid_id': request.form.get('orcid', ''),
        'image': request.form.get('image', ''),
        'address': request.form.get('address', ''),
        'description': request.form.get('description', ''),
        'imprint': request.form.get('imprint', ''),
        'legal_notice': request.form.get('legalnotice', '')}

    current_tab = 'nav-' + form_data['category']
    redirect_base = url_for('admin') + current_tab
    try:
        new_id = Admin.add_entry(form_data)
        flash(_('Entry added successfully!'), 'success')
        return redirect(f"{redirect_base}/{current_tab}{new_id}")
    except Admin.TooManyMainProjects:
        flash(
            f'Error adding entry {form_data["name"]}: '
            'Only one main project allowed',
            'danger')
    except Exception as e:
        flash(f'Error adding entry {form_data["name"]}: {e}', 'danger')

    return redirect(redirect_base)


@app.route('/edit_entry', methods=['POST', 'GET'])
@login_required
def edit_entry() -> Response:
    check_manager_user()
    form_data = {
        'config_id': request.form.get('config_id', type=int),
        'name': request.form.get('name', ''),
        'email': request.form.get('mail', ''),
        'website': request.form.get('website', ''),
        'orcid_id': request.form.get('orcid', ''),
        'image': request.form.get('image', ''),
        'address': request.form.get('address', ''),
        'description': request.form.get('description', ''),
        'imprint': request.form.get('imprint', ''),
        'legal_notice': request.form.get('legalnotice', '')}
    try:
        Admin.edit_entry(form_data)
        flash(f'"{form_data["name"]}" updated successfully', 'success')
    except EntryNotFound:
        flash(f'No config entry found with ID {form_data["config_id"]}',
              'danger')
    except Exception as e:
        flash(f'Error updating "{form_data["name"]}": {e}', 'danger')

    return redirect(
        url_for(
            'admin',
            entry=request.form.get('current_entry'),
            tab=request.form.get('current_tab')))


@app.route('/admin/edit_map', methods=['POST'])
@login_required
def edit_map() -> Response:
    check_manager_user()
    form_data = {
        'name': request.form.get('name', ''),
        'display_name': request.form.get('displayname', ''),
        'sortorder': request.form.get('inputorder', ''),
        'tilestring': request.form.get('description', ''),
        'map_id': request.form.get('map_id')}

    if not form_data['map_id']:
        flash('Map ID is required', 'danger')
        return redirect(url_for('admin'))
    if not check_if_map_id_exist(int(form_data['map_id'])):
        flash(f'Map with ID {form_data["map_id"]} not found', 'danger')
        return redirect(url_for('admin'))

    try:
        Admin.update_map(form_data)
        flash('Map updated successfully', 'success')
    except Exception as e:
        flash(f'Error updating map {form_data["map_id"]}: {e}', 'danger')
    return redirect(url_for('admin'))


@app.route('/admin/add_map', methods=['POST'])
@login_required
def add_map() -> Response:
    check_manager_user()
    data = {
        'name': request.form.get('name'),
        'display_name': request.form.get('displayname'),
        'sort_order': request.form.get('inputorder'),
        'tile_string': request.form.get('description')}
    try:
        map_id = Admin.add_new_map(data)
        flash(
            f"Map {data['name']} with ID {map_id} added successfully!",
            'success')
    except Exception as e:
        flash(f"Error adding map {data['name']}: {e}", 'danger')
    return redirect(url_for('admin'))


@app.route('/admin/delete_map/<int:map_id>')
@login_required
def delete_map(map_id: int) -> Response:
    check_manager_user()
    try:
        Admin.delete_map(map_id)
        flash('Map deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting map: {str(e)}', 'danger')
    return redirect(url_for('admin'))


@app.route('/admin/choose_index_background', methods=['POST'])
def choose_index_background() -> Response:
    settings = {
        'index_map': request.form.get('mapselection'),
        'index_img': request.form.get('default_img'),
        'img_map': request.form.get('imgmap'),
        'greyscale': request.form.get('greyscale') == 'on'}
    Admin.set_index_background(settings)
    return redirect(url_for('admin'))


@app.route('/admin/select_entities', methods=['POST'])
def select_entities() -> Response:
    if request.method == 'POST':
        Admin.set_shown_entities(request.form.getlist('selected_entities'))
        flash(_('set shown entities'), 'info')
    return redirect(url_for('admin'))


@app.route('/admin/deselect_entities', methods=['POST'])
def deselect_entities() -> Response:
    if request.method == 'POST':
        Admin.set_hidden_entities(request.form.getlist('selected_entities'))
        flash(_('set hidden entities'), 'info')
    return redirect(url_for('admin'))


# Todo: This reset button is only here for development purpose.
@app.route('/reset')
@login_required
def reset() -> Response:
    # Avoid exposing password in command line
    env = os.environ.copy()
    env['PGPASSWORD'] = current_app.config['DATABASE_PASS']
    subprocess.run([
        'psql',
        '-U', current_app.config['DATABASE_USER'],
        '-h', current_app.config['DATABASE_HOST'],
        '-p', str(current_app.config['DATABASE_PORT']),
        '-d', current_app.config['DATABASE_NAME'],
        '-f', os.path.join(current_app.root_path, 'sql', 'reset.sql')],
        env=env,
        check=True)

    return redirect(url_for('admin'))


def check_manager_user() -> None:
    if current_user.group not in ['admin', 'manager']:
        abort(403)

# @app.route('/sortlinks', methods=['POST'])
# def sort_links() -> Response:
#     @login_required
#     def reset_():
#         if current_user.group not in ['admin', 'manager']:
#             abort(403)
#
#     data = request.get_json()
#     criteria = data['criteria']
#     table = data['table']
#
#     for row in criteria:
#         g.cursor.execute(
#             f'UPDATE tng.{table} SET sortorder = %(order)s  WHERE id = %(
#             id)s',
#             {'id': row['id'], 'order': row['order'], 'table': table})
#     return jsonify({'status': 'ok'})
