import os
import subprocess
from typing import Any, Optional

from flask import (
    abort, current_app, flash, g, jsonify, redirect, render_template,
    request, url_for)
from flask_babel import gettext as _
from flask_login import current_user, login_required
from werkzeug import Response

from histarchexplorer import app, cache
from histarchexplorer.api.api_access import ApiAccess
from histarchexplorer.database.admin import update_sort_order
from histarchexplorer.database.map import check_if_map_id_exist
from histarchexplorer.models.admin import Admin
from histarchexplorer.utils.view_util import find_children_by_id
from histarchexplorer.views.views import type_tree


def check_manager_user() -> None:
    if current_user.group not in ['admin', 'manager']:
        abort(403)


@app.route('/admin/')
@app.route('/admin/<tab>')
@app.route('/admin/<tab>/<entry>')
@login_required
def admin(tab: Optional[str] = None, entry: Optional[str] = None) -> str:
    check_manager_user()
    tabs = [
        {'label': _('main-project'), 'target': 'nav-main-project',
         'id': g.config_classes['main-project']},
        {'label': _('projects'), 'target': 'nav-projects',
         'id': g.config_classes['project']},
        {'label': _('persons'), 'target': 'nav-persons',
         'id': g.config_classes['person']},
        {'label': _('institutions'), 'target': 'nav-institutions',
         'id': g.config_classes['institution']},
        {'label': _('attributes'), 'target': 'nav-attributes',
         'id': g.config_classes['attribute']}]

    if not tab and tabs:
        tab = tabs[0]['target']
    for tab_item in tabs:
        tab_item['is_active'] = tab_item['target'] == tab

    cs_type_id: Optional[int] = None
    cs_type_name: Optional[str] = None
    case_study_children: list[dict[str, str]] | None = []

    if g.settings.case_study_type_id:
        try:
            cs_type_id = int(g.settings.case_study_type_id)
            details = Admin.get_openatlas_entity(cs_type_id)
            if details:
                cs_type_name = details.name

            case_study_children = find_children_by_id(
                type_tree().get_json(),
                cs_type_id)
        except (ValueError, TypeError) as e:
            app.logger.error('Error processing case study type ID: %s', e)

    return render_template(
        "admin.html",
        tabs=tabs,
        processed_entities_by_tab=Admin.process_entities_by_tab(tabs, entry),
        processed_links_by_entity=Admin.process_links_by_entity(),
        processed_properties_by_tab=Admin.process_properties_by_tab(tabs),
        processed_roles=Admin.process_roles(),
        processed_target_nodes=Admin.process_target_nodes(),
        maps=Admin.get_maps(),
        settings=g.settings.get_map_settings(),
        class_items={
            k: v for k, v in
            ApiAccess.get_entities_count_by_case_studies().items()
            if k not in app.config['CLASSES_TO_SKIP']},
        shown_classes=g.settings.shown_classes,
        hidden_classes=g.settings.hidden_classes,
        initial_case_study_type_id=cs_type_id,
        initial_case_study_type_name=cs_type_name,
        case_study_children=case_study_children)


@app.route('/admin/delete_link/<int:link_id>/<tab>/<entry>', methods=['GET'])
@login_required
def delete_link(link_id: int, tab: str, entry: str) -> Response:
    check_manager_user()
    Admin.delete_link(link_id)
    flash(_('Link deleted successfully'), 'success')
    return redirect(url_for('admin', tab=tab, entry=entry))


@app.route('/admin/add_link/', methods=['GET'])
@login_required
def add_link() -> Response:
    check_manager_user()

    try:
        raw_domain = request.args.get('domain')
        raw_range = request.args.get('range')
        raw_prop = request.args.get('property')
        raw_role = request.args.get('role', '0')

        if (raw_domain is not None and
                raw_range is not None and
                raw_prop is not None):

            link_data = {
                'domain': int(raw_domain),
                'range': int(raw_range),
                'prop': int(raw_prop),
                'role': int(raw_role),
                'sortorder': Admin.check_sortorder()}

            Admin.add_link(link_data)
            flash(_('Link added successfully'), 'success')
        else:
            raise ValueError("Missing required link parameters")

    except (ValueError, TypeError) as e:
        app.logger.warning("Invalid link attempt: %s", e)
        flash(_('Failed to add link: Invalid data provided'), 'error')

    return redirect(
        url_for(
            'admin',
            tab=request.args.get('tab', ''),
            entry=request.args.get('entry', '')))


@app.route('/admin/add_entry', methods=['POST'])
@login_required
def add_entry() -> Response:
    check_manager_user()
    case_study_str = request.form.get('case_study')
    form_data: dict[str, str | int] = {
        'category': request.form.get('category', ''),
        'name': request.form.get('name', ''),
        'acronym': request.form.get('acronym', ''),
        'email': request.form.get('email', ''),
        'website': request.form.get('website', ''),
        'orcid_id': request.form.get('orcid_id', ''),
        'image': request.form.get('image', ''),
        'address': request.form.get('address', ''),
        'description': request.form.get('description', ''),
        'imprint': request.form.get('imprint', ''),
        'legal_notice': request.form.get('legal_notice', ''),
        'case_study': int(case_study_str)
        if case_study_str and case_study_str.isdigit() else 0}
    current_tab = f'nav-{form_data["category"]}'
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


@app.route('/edit_entry', methods=['POST', 'GET'])
@login_required
def edit_entry() -> Response:
    check_manager_user()

    config_id = request.form.get('config_id', type=int)
    name = request.form.get('name', '')
    cs_raw = request.form.get('case_study')
    case_study: int | None = int(cs_raw) \
        if cs_raw and cs_raw.isdigit() else None

    if config_id is None:
        flash(_('Configuration ID is required'), 'danger')
        return redirect(url_for('admin'))

    form_data: dict[str, str | int] = {
        'config_id': config_id,
        'name': name,
        'acronym': request.form.get('acronym', ''),
        'email': request.form.get('email', ''),
        'website': request.form.get('website', ''),
        'orcid_id': request.form.get('orcid_id', ''),
        'image': request.form.get('image', ''),
        'address': request.form.get('address', ''),
        'description': request.form.get('description', ''),
        'imprint': request.form.get('imprint', ''),
        'legal_notice': request.form.get('legal_notice', ''),
        'case_study': case_study}

    try:
        Admin.edit_entry(form_data)
        flash(_('"%(name)s" updated successfully', name=name), 'success')
    except Exception as e:
        app.logger.error("Entry update failed: %s", e)
        flash(
            _('Error updating "%(name)s": %(error)s',
              name=name, error=str(e)), 'danger')

    return redirect(
        url_for(
            'admin',
            entry=request.form.get('current_entry'),
            tab=request.form.get('current_tab')))


@app.route('/admin/edit_map', methods=['POST'])
@login_required
def edit_map() -> Response:
    check_manager_user()

    raw_map_id = request.form.get('map_id')
    name = request.form.get('name', '')
    display_name = request.form.get('displayname', '')
    sort_order = request.form.get('inputorder', '0')
    tile_string = request.form.get('description', '')

    if not raw_map_id:
        flash(_('Map ID is required'), 'danger')
        return redirect(url_for('admin'))

    try:
        map_id = int(raw_map_id)
        if not check_if_map_id_exist(map_id):
            flash(_(f'Map with ID {map_id} not found'), 'danger')
            return redirect(url_for('admin'))

        form_data: dict[str, str] = {
            'name': name,
            'display_name': display_name,
            'sortorder': sort_order,
            'tilestring': tile_string,
            'map_id': str(map_id)}

        Admin.update_map(form_data)
        flash(_('Map updated successfully'), 'success')

    except ValueError:
        flash(_('Invalid Map ID format'), 'danger')
    except Exception as e:
        app.logger.error("Map update failed: %s", e)
        flash(_('Error updating map: %(error)s', error=str(e)), 'danger')

    return redirect(url_for('admin'))


@app.route('/admin/add_map', methods=['POST'])
@login_required
def add_map() -> Response:
    check_manager_user()

    name = request.form.get('name')
    display_name = request.form.get('displayname')
    sort_order = request.form.get('inputorder', '0')
    tile_string = request.form.get('description')

    if not name or not display_name or not tile_string:
        flash(
            _('Error: Name, Display Name and Description are required'),
            'danger')
        return redirect(url_for('admin'))

    data: dict[str, str] = {
        'name': name,
        'display_name': display_name,
        'sort_order': sort_order,
        'tile_string': tile_string}
    try:
        map_id = Admin.add_new_map(data)
        flash(
            f"Map {data['name']} with ID {map_id} added successfully!",
            'success')
    except Exception as e:
        app.logger.error("Failed to add map: %s", e)
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
@login_required
def choose_index_background() -> Response:
    check_manager_user()

    index_map = request.form.get('mapselection', '')
    index_img = request.form.get('default_img', '')
    img_map = request.form.get('imgmap', '')
    greyscale = request.form.get('greyscale') == 'on'

    settings: dict[str, Any] = {
        'index_map': index_map,
        'index_img': index_img,
        'img_map': img_map,
        'greyscale': greyscale}
    try:
        Admin.set_index_background(settings)
        flash(_('Index background updated successfully'), 'success')
    except Exception as e:
        app.logger.error("Failed to set index background: %s", e)
        flash(_('Error updating settings'), 'error')

    return redirect(url_for('admin'))


@app.route('/admin/select_entities', methods=['POST'])
@login_required
def select_entities() -> Response:
    check_manager_user()
    if request.method == 'POST':
        Admin.set_shown_classes(request.form.getlist('selected_entities'))
        flash(_('set shown entities'), 'info')
    return redirect(url_for('admin'))


@app.route('/admin/deselect_entities', methods=['POST'])
@login_required
def deselect_entities() -> Response:
    check_manager_user()
    if request.method == 'POST':
        Admin.set_hidden_classes(request.form.getlist('selected_entities'))
        flash(_('set hidden entities'), 'info')
    return redirect(url_for('admin'))


@app.route('/sortlinks', methods=['POST'])
@login_required
def sort_links() -> tuple[Response, int] | Response:
    check_manager_user()

    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data received'}), 400

        table = data.get('table')
        if table not in {'links', 'maps'}:
            return jsonify({'error': f'Invalid table: {table}'}), 400

        criteria = data.get('criteria')
        if not isinstance(criteria, list):
            return jsonify({'error': 'Criteria must be a list'}), 400

        update_sort_order(
            table,
            [{'order': int(row['order']), 'id': int(row['id'])}
             for row in criteria])
    except (ValueError, KeyError):
        return jsonify({'error': 'Invalid data format.'}), 400
    except Exception as _:
        return jsonify({'error': 'Database error occurred'}), 500
    return jsonify({'status': 'ok'})


@app.route('/admin/update_case_study_id/<int:id_>', methods=['POST'])
@login_required
def update_case_study_id(id_: int) -> Response:
    check_manager_user()
    if request.method == 'POST':
        validation_result = Admin.check_case_study_type_id(id_)
        if validation_result['is_valid']:
            Admin.update_case_study_id_setting(id_)
            flash(_('updated case study id successfully'), 'info')
        else:
            message = _(
                'Invalid Case Study ID. Must be a positive integer '
                'and its entity type must be "type".')
            flash(message, 'error')
    return redirect(url_for('admin'))


@app.route('/admin/check_case_study_id_ajax/<int:entity_id>', methods=['GET'])
@login_required
def check_case_study_id_ajax(entity_id: int) -> Response:
    check_manager_user()
    result = Admin.check_case_study_type_id(entity_id)
    return jsonify(result)


# Todo: remove for production
@app.route('/reset')
def reset() -> Response:
    make_reset()
    flash(_('reset database'), 'info')
    return redirect(url_for('admin'))


def make_reset() -> None:
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


@app.route('/admin/clear-cache')
@login_required
def clear_cache() -> Response:
    cache.clear()
    flash(_('cache cleared'), 'success')
    return redirect(url_for('admin'))


@app.route("/admin/warm-entity-cache")
@login_required
def warm_entity_cache() -> Response:
    trigger_cache_warmup(False)
    flash(_("Cache warmup started in background (refresh mode)"), 'success')
    return redirect(url_for('admin'))


@app.route("/admin/refresh-entity-cache")
@login_required
def refresh_entity_cache() -> Response:
    trigger_cache_warmup(True)
    flash(_("Cache warmup started in background."), 'success')
    return redirect(url_for('admin'))


def trigger_cache_warmup(refresh: bool = False) -> None:
    """Trigger external cache warm-up process."""
    try:
        args: list[str] = ["python3", "warm_entity_cache.py"]
        if refresh:
            args.append("--refresh")
        if hasattr(g, "case_study_ids") and g.case_study_ids:
            ids_str: str = " ".join(str(i) for i in g.case_study_ids)
            args.extend(["--case-studies", ids_str])
        with subprocess.Popen(
                args,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL) as _proc:
            pass
    except Exception as e:
        flash(str(e), "error")
        abort(404)


@app.route('/admin/refresh-system-cache')
@login_required
def refresh_system_cache() -> Response:
    cache.delete_memoized(ApiAccess.get_type_tree)
    cache.delete_memoized(ApiAccess.get_files_of_entities)
    cache.delete_memoized(ApiAccess.get_system_class_count)
    cache.delete_memoized(ApiAccess.get_entities_count_by_case_studies)

    ApiAccess.get_type_tree()
    ApiAccess.get_files_of_entities()
    ApiAccess.get_entities_count_by_case_studies()
    for case_study in g.case_study_ids:
        ApiAccess.get_entities_count_by_case_studies(case_study)

    flash(_('system cache refreshed'), 'success')
    return redirect(url_for('admin'))
