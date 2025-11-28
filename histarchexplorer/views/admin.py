import os
import subprocess
from typing import Optional

from flask import (
    abort, current_app, flash, g, jsonify, redirect, render_template,
    request, url_for)
from flask_babel import lazy_gettext as _
from flask_login import current_user, login_required
from werkzeug import Response

from histarchexplorer import app, cache
from histarchexplorer.api.api_access import ApiAccess
from histarchexplorer.database.map import check_if_map_id_exist
from histarchexplorer.models.admin import Admin, EntryNotFound
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
    for tab_ in tabs:
        tab_['is_active'] = (tab_['target'] == tab)

    initial_case_study_type_id = None
    initial_case_study_type_name = None
    if g.settings.case_study_type_id:
        initial_case_study_type_id = int(g.settings.case_study_type_id)
        details = Admin.get_openatlas_entity(initial_case_study_type_id)
        if details:
            initial_case_study_type_name = details.name

    case_study_children = find_children_by_id(
        type_tree().get_json(),
        initial_case_study_type_id)

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
        initial_case_study_type_id=initial_case_study_type_id,
        initial_case_study_type_name=initial_case_study_type_name,
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
    case_study_str = request.form.get('case_study')
    form_data = {
        'category': request.form.get('category', ''),
        'name': request.form.get('name', ''),
        'acronym': request.form.get('acronym', ''),
        'email': request.form.get('mail', ''),
        'website': request.form.get('website', ''),
        'orcid_id': request.form.get('orcid', ''),
        'image': request.form.get('image', ''),
        'address': request.form.get('address', ''),
        'description': request.form.get('description', ''),
        'imprint': request.form.get('imprint', ''),
        'legal_notice': request.form.get('legalnotice', ''),
        'case_study': int(case_study_str)
        if case_study_str and case_study_str.isdigit() else 0}
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
    case_study_raw = request.form.get('case_study')
    case_study = int(case_study_raw) if case_study_raw else None
    print(request.form)
    form_data = {
        'config_id': request.form.get('config_id', type=int),
        'name': request.form.get('name', ''),
        'acronym': request.form.get('acronym', ''),
        'email': request.form.get('email', ''),
        'website': request.form.get('website', ''),
        'orcid_id': request.form.get('orcid_id', ''),
        'image': request.form.get('image', ''),
        'address': request.form.get('address', ''),
        'description': request.form.get('description', ''),
        'imprint': request.form.get('imprint', ''),
        'legal_notice': request.form.get('legalnotice', ''),
        'case_study': case_study}
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
        'name': request.form.get('name'),
        'display_name': request.form.get('displayname'),
        'sortorder': request.form.get('inputorder'),
        'tilestring': request.form.get('description'),
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
@login_required
def choose_index_background() -> Response:
    check_manager_user()
    settings = {
        'index_map': request.form.get('mapselection'),
        'index_img': request.form.get('default_img'),
        'img_map': request.form.get('imgmap'),
        'greyscale': request.form.get('greyscale') == 'on'}
    Admin.set_index_background(settings)
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


def make_reset():
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
def clear_cache():
    cache.clear()
    flash(_('cache cleared'), 'success')
    return redirect(url_for('admin'))


@app.route("/admin/warm-entity-cache")
@login_required
def warm_entity_cache():
    trigger_cache_warmup(False)
    flash(_("Cache warmup started in background (refresh mode)"), 'success')
    return redirect(url_for('admin'))


@app.route("/admin/refresh-entity-cache")
@login_required
def refresh_entity_cache():
    trigger_cache_warmup(True)
    flash(_("Cache warmup started in background."), 'success')
    return redirect(url_for('admin'))


def trigger_cache_warmup(refresh: bool = False):
    """Trigger external cache warm-up process."""
    try:
        args = ["python3", "warm_entity_cache.py"]
        print(' '.join([str(ids) for ids in g.case_study_ids]))
        if refresh:
            args.append("--refresh")
        if g.case_study_ids:
            args.append(
                "--case-studies "
                f"{' '.join([str(ids) for ids in g.case_study_ids])}")
        subprocess.Popen(
            args,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL)
    except Exception as e:
        flash(str(e), "error")
        return abort(404)


@app.route('/admin/refresh-system-cache')
@login_required
def refresh_system_cache():
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
