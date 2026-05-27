import os
import json
import re
import subprocess
from typing import Optional
from datetime import datetime
from werkzeug.utils import secure_filename
from PIL import Image

from flask import (
    abort, current_app, flash, g, jsonify, redirect, render_template,
    request, url_for, send_file, send_from_directory)
from flask_babel import gettext as _
from flask_login import current_user, login_required
from werkzeug import Response

from histarchexplorer import app, cache
from histarchexplorer.api.api_access import ApiAccess
from histarchexplorer.database.admin import (
    update_sort_order, add_logo_to_db, delete_logo_from_db, rename_logo_in_db,
    add_asset_to_db, delete_asset_from_db, rename_asset_in_db,
    add_file_to_db, delete_file_from_db, rename_file_in_db)
from histarchexplorer.database.map import check_if_map_id_exist
from histarchexplorer.models.admin import Admin
from histarchexplorer.utils.view_util import find_children_by_id
from histarchexplorer.views.views import type_tree


def check_manager_user() -> None:
    if current_user.group not in ['admin', 'manager']:
        abort(403)


def _redirect_to_admin_tab(default_tab: str) -> Response:
    tab = request.form.get('active_sidebar', default_tab)
    return redirect(url_for('admin', tab=tab))


@app.route('/admin/')
@app.route('/admin/<tab>')
@app.route('/admin/<tab>/<entry>')
@login_required
def admin(tab: Optional[str] = None, entry: Optional[str] = None) -> str:
    check_manager_user()
    project_tabs = [
        {'label': _('main-project'), 'target': 'nav-main-project',
         'id': g.config_classes['main-project']},
        {'label': _('projects'), 'target': 'nav-projects',
         'id': g.config_classes['project']}]

    stakeholder_tabs = [
        {'label': _('persons'), 'target': 'nav-persons',
         'id': g.config_classes['person']},
        {'label': _('institutions'), 'target': 'nav-institutions',
         'id': g.config_classes['institution']},
        {'label': _('attributes'), 'target': 'nav-attributes',
         'id': g.config_classes['attribute']}]

    all_tabs = project_tabs + stakeholder_tabs

    # Determine which main sidebar section should be active
    active_main_sidebar_id = 'sidebar-general-settings-group'  # Default

    if tab:
        if any(t['target'] == tab for t in project_tabs):
            active_main_sidebar_id = 'sidebar-projects-content'
        elif any(t['target'] == tab for t in stakeholder_tabs):
            active_main_sidebar_id = 'sidebar-stakeholders-content'
        else:
            match tab:
                case ('sidebar-maps' | 'sidebar-index-page-options' |
                      'sidebar-database' | 'sidebar-cache-options' |
                      'sidebar-content-group' | 'sidebar-logo-management' |
                      'sidebar-icon-management' |
                      'sidebar-menu-management' | 'sidebar-footer-content' |
                      'sidebar-file-management-group' | 'sidebar-assets' |
                      'sidebar-legal-notice' | 'sidebar-licenses' |
                      'sidebar-team' | 'sidebar-about-publications' |
                      'sidebar-projects-content' | 'sidebar-stakeholders-content' |
                      'sidebar-colors' | 'sidebar-type-divisions' |
                      'sidebar-visibility-settings' |
                      'sidebar-general-settings-group' | 'sidebar-about-content' |
                      'sidebar-outcome' | 'sidebar-search-content'):
                    active_main_sidebar_id = tab

                case _:
                    pass

    any_active_tab = False
    for tab_item in all_tabs:
        tab_item['is_active'] = tab_item['target'] == tab
        if tab_item['is_active']:
            any_active_tab = True

    if not any_active_tab:
        if active_main_sidebar_id == 'sidebar-projects-content':
            project_tabs[0]['is_active'] = True
        elif active_main_sidebar_id == 'sidebar-stakeholders-content':
            stakeholder_tabs[0]['is_active'] = True

    cs_type_id: Optional[int] = None
    cs_type_name: Optional[str] = None
    case_study_children: list[dict[str, str]] | None = []

    if g.settings.case_study_type_id:
        try:
            cs_type_id = int(g.settings.case_study_type_id)
            details = Admin.get_openatlas_entity(cs_type_id)
            if details:
                cs_type_name = details['name']

            case_study_children = find_children_by_id(
                type_tree().get_json(),
                cs_type_id)
        except (ValueError, TypeError) as e:
            app.logger.error('Error processing case study type ID: %s', e)

    admin_instance = Admin()
    all_logos = admin_instance.get_all_logos_with_ids()
    all_team = admin_instance.get_all_teams_with_ids()
    all_assets = admin_instance.get_all_assets_with_ids()
    selected_footer_logos = g.settings.footer_logos

    return render_template(
        "admin.html",
        project_tabs=project_tabs,
        stakeholder_tabs=stakeholder_tabs,
        tabs=all_tabs,
        admin_instance=admin_instance,
        processed_entities_by_tab=admin_instance.process_entities_by_tab(
            all_tabs,
            entry),
        processed_links_by_entity=admin_instance.process_links_by_entity(),
        processed_properties_by_tab=admin_instance.process_properties_by_tab(
            all_tabs),
        processed_roles=admin_instance.process_roles(),
        processed_target_nodes=admin_instance.process_target_nodes(),
        maps=Admin.get_maps(),
        settings=g.settings,
        class_items={
            k: v for k, v in
            ApiAccess.get_entities_count_by_case_studies().items()
            if k not in app.config['CLASSES_TO_SKIP']},
        shown_classes=g.settings.shown_classes,
        hidden_classes=g.settings.hidden_classes,
        initial_case_study_type_id=cs_type_id,
        initial_case_study_type_name=cs_type_name,
        case_study_children=case_study_children,
        active_main_sidebar_id=active_main_sidebar_id,
        licenses=admin_instance.licenses,
        all_logos=all_logos,
        all_team=all_team,
        all_assets=all_assets,
        selected_footer_logos=selected_footer_logos)


@app.route('/admin/update_type_divisions', methods=['POST'])
@login_required
def update_type_divisions() -> Response:
    check_manager_user()
    new_type_divisions = {}
    indices = {
        key.split('_')[-1] for key in request.form if
        key.startswith('label_')}
    for index in indices:
        label = request.form.get(f'label_{index}')
        if not label:
            continue

        ids_str = request.form.get(f'ids_{index}', '')
        try:
            ids = [int(i.strip()) for i in ids_str.split(',') if i.strip()]
        except ValueError:
            flash(_(
                'Invalid ID format for label "%(label)s". Please use '
                'comma-separated integers.', label=label), 'danger')
            return _redirect_to_admin_tab('sidebar-type-divisions')

        new_type_divisions[label] = {
            'icon_type': request.form.get(f'icon_type_{index}'),
            'icon_value': request.form.get(f'icon_value_{index}'),
            'ids': ids
        }

    g.settings.type_divisions = new_type_divisions
    try:
        g.settings.save_to_db()
        flash(_('Type divisions updated successfully.'), 'success')
    except Exception as e:
        app.logger.error("Failed to update type divisions: %s", e)
        flash(_('Error updating type divisions'), 'error')

    return _redirect_to_admin_tab('sidebar-type-divisions')


@app.route('/admin/update_entity_colors', methods=['POST'])
@login_required
def update_entity_colors() -> Response:
    check_manager_user()
    colors = {}
    for key, value in request.form.items():
        if key.startswith('entity_colors-'):
            entity_type = key.split('-')[1]
            colors[entity_type] = value
    g.settings.entity_colors = colors
    try:
        g.settings.save_to_db()
        flash(_('Entity colors updated successfully.'), 'success')
    except Exception as e:
        app.logger.error("Failed to update entity colors: %s", e)
        flash(_('Error updating entity colors'), 'error')
    return _redirect_to_admin_tab('sidebar-colors')


@app.route('/admin/add_available_color', methods=['POST'])
@login_required
def add_available_color() -> Response:
    check_manager_user()
    new_color = request.form.get('new_color')
    if (new_color and re.match(
            r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$', new_color)):
        if new_color not in g.settings.available_colors:
            g.settings.available_colors.append(new_color)
            try:
                g.settings.save_to_db()
                flash(_('Color added successfully.'), 'success')
            except Exception as e:
                app.logger.error("Failed to add color: %s", e)
                flash(_('Error adding color'), 'error')
        else:
            flash(_('Color already exists.'), 'warning')
    else:
        flash(_('Invalid HEX code.'), 'danger')
    return _redirect_to_admin_tab('sidebar-colors')


@app.route('/admin/delete_available_color', methods=['POST'])
@login_required
def delete_available_color() -> Response:
    check_manager_user()
    color_to_delete = request.form.get('color_to_delete')
    if color_to_delete in g.settings.available_colors:
        g.settings.available_colors.remove(color_to_delete)
        try:
            g.settings.save_to_db()
            flash(_('Color deleted successfully.'), 'success')
        except Exception as e:
            app.logger.error("Failed to delete color: %s", e)
            flash(_('Error deleting color'), 'error')
    return _redirect_to_admin_tab('sidebar-colors')


@app.route('/admin/update_menu_management', methods=['POST'])
@login_required
def update_menu_management() -> Response:
    check_manager_user()
    menu_data = {}
    for item_key in g.settings.menu_management.keys():
        menu_data[item_key] = {
            'show': request.form.get(f'show_{item_key}') == 'on',
            'page_type': request.form.get(f'page_type_{item_key}', 'default')
        }

    g.settings.menu_management = menu_data

    try:
        g.settings.save_to_db()
        flash(_('Menu settings updated successfully.'), 'success')
    except Exception as e:
        app.logger.error("Failed to update menu settings: %s", e)
        flash(_('Error updating menu settings'), 'error')

    return _redirect_to_admin_tab('sidebar-menu-management')


@app.route('/admin/update_legal_notice', methods=['POST'])
@login_required
def update_legal_notice() -> Response:
    check_manager_user()
    legal_notice_data = {}

    for lang_code in g.available_languages.keys():
        legal_notice_data[lang_code] = request.form.get(
            f'legal_notice_{lang_code}', '')

    g.settings.legal_notice = legal_notice_data

    try:
        g.settings.save_to_db()
        flash(_('Legal notice updated successfully.'), 'success')
    except Exception as e:
        app.logger.error("Failed to update legal notice: %s", e)
        flash(_('Error updating settings'), 'error')

    return _redirect_to_admin_tab('sidebar-legal-notice')


@app.route('/admin/upload_logo', methods=['POST'])
@login_required
def upload_logo():
    check_manager_user()
    if 'logo_file' not in request.files:
        flash(_('No file part'), 'danger')
        return _redirect_to_admin_tab('sidebar-logo-management')

    file = request.files['logo_file']
    if file.filename == '':
        flash(_('No selected file'), 'danger')
        return _redirect_to_admin_tab('sidebar-logo-management')

    if file:
        filename = secure_filename(file.filename)
        upload_path = os.path.join(app.root_path, '..', 'uploads', 'logos')
        os.makedirs(upload_path, exist_ok=True)
        file.save(os.path.join(upload_path, filename))
        add_logo_to_db(filename, is_default=False)
        flash(_('Logo "%(name)s" uploaded successfully.', name=filename),
              'success')

    return _redirect_to_admin_tab('sidebar-logo-management')


@app.route('/admin/rename_logo', methods=['POST'])
@login_required
def rename_logo():
    check_manager_user()
    old_name = request.form.get('old_name')
    new_name = request.form.get('new_name')

    if not old_name or not new_name:
        flash(_('Invalid request for renaming.'), 'danger')
        return _redirect_to_admin_tab('sidebar-logo-management')

    static_path = os.path.join(app.static_folder, 'images', 'logos')
    uploads_path = os.path.join(app.root_path, '..', 'uploads', 'logos')

    old_filepath_static = os.path.join(static_path, secure_filename(old_name))
    old_filepath_uploads = os.path.join(
        uploads_path, secure_filename(old_name))

    if os.path.exists(old_filepath_static):
        flash(_('Cannot rename default logos.'), 'danger')
        return _redirect_to_admin_tab('sidebar-logo-management')
    elif os.path.exists(old_filepath_uploads):
        old_filepath = old_filepath_uploads
        new_filepath = os.path.join(uploads_path, secure_filename(new_name))
    else:
        flash(_('Original file not found.'), 'danger')
        return _redirect_to_admin_tab('sidebar-logo-management')

    if os.path.exists(new_filepath):
        flash(_('A file with the new name already exists.'), 'danger')
        return _redirect_to_admin_tab('sidebar-logo-management')

    try:
        os.rename(old_filepath, new_filepath)
        rename_logo_in_db(old_name, new_name)
        flash(_('Logo renamed from "%(old)s" to "%(new)s".', old=old_name,
                new=new_name), 'success')
    except OSError as e:
        flash(_('Error renaming file: %(error)s', error=e), 'danger')

    return _redirect_to_admin_tab('sidebar-logo-management')


@app.route('/admin/delete_logo', methods=['POST'])
@login_required
def delete_logo():
    check_manager_user()
    filename = request.form.get('filename')
    if not filename:
        flash(_('No filename specified for deletion.'), 'danger')
        return _redirect_to_admin_tab('sidebar-logo-management')

    uploads_path = os.path.join(app.root_path, '..', 'uploads', 'logos')
    filepath_uploads = os.path.join(uploads_path, secure_filename(filename))

    if os.path.exists(filepath_uploads):
        try:
            os.remove(filepath_uploads)
            delete_logo_from_db(filename) # This will delete the row
            flash(_('Logo "%(name)s" deleted successfully.', name=filename),
                  'success')
        except OSError as e:
            flash(_('Error deleting file: %(error)s', error=e), 'danger')
    else:
        delete_logo_from_db(filename) # This will set is_active = FALSE
        flash(_('Default logo "%(name)s" deactivated.', name=filename), 'success')

    return _redirect_to_admin_tab('sidebar-logo-management')


@app.route('/admin/set_main_logo', methods=['POST'])
@login_required
def set_main_logo() -> Response:
    check_manager_user()
    filename = request.form.get('filename')
    if not filename:
        flash(_('No filename specified.'), 'danger')
        return _redirect_to_admin_tab('sidebar-logo-management')

    g.settings.nav_logo = filename
    try:
        g.settings.save_to_db()
        flash(_('Main logo updated successfully.'), 'success')
    except Exception as e:
        app.logger.error("Failed to set main logo: %s", e)
        flash(_('Error updating settings'), 'error')

    return _redirect_to_admin_tab('sidebar-logo-management')


@app.route('/admin/set_favicon', methods=['POST'])
@login_required
def set_favicon() -> Response:
    check_manager_user()
    filename = request.form.get('filename')
    if not filename:
        flash(_('No filename specified.'), 'danger')
        return _redirect_to_admin_tab('sidebar-logo-management')

    # Check uploads first, then static
    uploads_path = os.path.join(app.root_path, '..', 'uploads', 'logos')
    static_path = os.path.join(app.static_folder, 'images', 'logos')

    logo_path = os.path.join(uploads_path, filename)
    if not os.path.exists(logo_path):
        logo_path = os.path.join(static_path, filename)

    target_dir = os.path.join(app.root_path, '..', 'uploads')
    os.makedirs(target_dir, exist_ok=True)
    favicon_path = os.path.join(target_dir, 'favicon.ico')

    try:
        with Image.open(logo_path) as img:
            img.save(favicon_path, 'ICO', sizes=[(32, 32)])
        flash(_('Favicon updated successfully.'), 'success')
    except Exception as e:
        app.logger.error(f"Failed to set favicon: {e}")
        flash(_('Error creating favicon: %(error)s', error=str(e)), 'danger')

    return _redirect_to_admin_tab('sidebar-logo-management')


@app.route('/admin/update_footer_content', methods=['POST'])
@login_required
def update_footer_content() -> Response:
    check_manager_user()
    selected_logo_ids = [
        int(logo_id) for logo_id in request.form.getlist('footer_logos')]
    ordered_logo_ids_str = request.form.get('footer_logo_order')

    if ordered_logo_ids_str:
        try:
            ordered_logo_ids = json.loads(ordered_logo_ids_str)
            # Ensure all selected logos are in the ordered list
            final_logo_ids = [
                int(id) for id in ordered_logo_ids if int(id) in selected_logo_ids]
            for logo_id in selected_logo_ids:
                if logo_id not in final_logo_ids:
                    final_logo_ids.append(logo_id)
            g.settings.footer_logos = final_logo_ids
        except json.JSONDecodeError:
            g.settings.footer_logos = selected_logo_ids
    else:
        g.settings.footer_logos = selected_logo_ids

    try:
        g.settings.save_to_db()
        flash(_('Footer logos updated successfully.'), 'success')
    except Exception as e:
        app.logger.error("Failed to update footer logos: %s", e)
        flash(_('Error updating footer logos'), 'error')

    return _redirect_to_admin_tab('sidebar-footer-content')


@app.route('/admin/add_license', methods=['POST'])
@login_required
def add_license():
    check_manager_user()
    spdx_id = request.form.get('spdx_id')
    uri = request.form.get('uri')
    label = request.form.get('label')
    category = request.form.get('category')
    Admin.add_license(spdx_id, uri, label, category)
    flash(_('License added successfully.'), 'success')
    return _redirect_to_admin_tab('sidebar-licenses')


@app.route('/admin/delete_license/<int:license_id>', methods=['POST'])
@login_required
def delete_license(license_id):
    check_manager_user()
    Admin.delete_license(license_id)
    flash(_('License deleted successfully.'), 'success')
    return _redirect_to_admin_tab('sidebar-licenses')


@app.route('/admin/update_logo_license', methods=['POST'])
@login_required
def update_logo_license() -> Response:
    check_manager_user()

    filename = request.form.get('filename', '')
    license_id = request.form.get('license_id', type=int)
    attribution = request.form.get('attribution', '')

    admin_instance = Admin()
    admin_instance.update_file_license(filename, license_id, attribution)

    flash(_('Logo license updated successfully.'), 'success')
    return _redirect_to_admin_tab('sidebar-logo-management')


@app.route('/admin/backup_db')
@login_required
def backup_db() -> Response:
    check_manager_user()
    try:
        db_name = current_app.config['DATABASE_NAME']
        db_user = current_app.config['DATABASE_USER']
        db_pass = current_app.config['DATABASE_PASS']
        db_host = current_app.config['DATABASE_HOST']
        db_port = str(current_app.config['DATABASE_PORT'])

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'backup_{db_name}_{timestamp}.sql'
        filepath = os.path.join('/tmp', filename)

        env = os.environ.copy()
        env['PGPASSWORD'] = db_pass

        command = [
            'pg_dump',
            '-U', db_user,
            '-h', db_host,
            '-p', db_port,
            '-d', db_name,
            '-n', 'tng',  # Todo: find better name
            '-f', filepath,
            '--clean',
            '--if-exists',
            '--create']

        subprocess.run(
            command,
            env=env,
            check=True,
            capture_output=True,
            text=True)

        return send_file(filepath, as_attachment=True)

    except subprocess.CalledProcessError as e:
        app.logger.error(f"Database backup failed: {e.stderr}")
        flash(_('Database backup failed. Check logs for details.'), 'danger')
    except Exception as e:
        app.logger.error(f"An unexpected error occurred during backup: {e}")
        flash(_('An unexpected error occurred. Check logs for details.'),
              'danger')

    return _redirect_to_admin_tab('sidebar-database')


@app.route('/admin/restore_db', methods=['POST'])
@login_required
def restore_db() -> Response:
    check_manager_user()
    if 'sql_file' not in request.files:
        flash(_('No file part'), 'danger')
        return _redirect_to_admin_tab('sidebar-database')

    file = request.files['sql_file']
    if file.filename == '':
        flash(_('No selected file'), 'danger')
        return _redirect_to_admin_tab('sidebar-database')

    if file and file.filename.endswith('.sql'):
        try:
            db_name = current_app.config['DATABASE_NAME']
            db_user = current_app.config['DATABASE_USER']
            db_pass = current_app.config['DATABASE_PASS']
            db_host = current_app.config['DATABASE_HOST']
            db_port = str(current_app.config['DATABASE_PORT'])

            filename = secure_filename(file.filename)
            filepath = os.path.join('/tmp', filename)
            file.save(filepath)

            env = os.environ.copy()
            env['PGPASSWORD'] = db_pass

            psql_command = [
                'psql',
                '-U', db_user,
                '-h', db_host,
                '-p', db_port,
                '-d', db_name,
                '-c', 'DROP SCHEMA IF EXISTS tng CASCADE;',
                '-c', 'CREATE SCHEMA tng;',
                '-c', f'ALTER SCHEMA tng OWNER TO {db_user};']

            subprocess.run(
                psql_command,
                env=env,
                check=True,
                capture_output=True,
                text=True)

            restore_command = [
                'psql',
                '-U', db_user,
                '-h', db_host,
                '-p', db_port,
                '-d', db_name,
                '-f', filepath]

            subprocess.run(
                restore_command,
                env=env,
                check=True,
                capture_output=True,
                text=True)

            os.remove(filepath)
            flash(_('Database restored successfully.'), 'success')

        except subprocess.CalledProcessError as e:
            app.logger.error(f"Database restore failed: {e.stderr}")
            flash(_('Database restore failed. Check logs for details.'),
                  'danger')
        except Exception as e:
            app.logger.error(
                f"An unexpected error occurred during restore: {e}")
            flash(_('An unexpected error occurred. Check logs for details.'),
                  'danger')
    else:
        flash(_('Invalid file type. Please upload a .sql file.'), 'danger')

    return _redirect_to_admin_tab('sidebar-database')


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
        params = {
            'domain': request.args.get('domain', type=int),
            'range': request.args.get('range', type=int),
            'prop': request.args.get('property', type=int),
            'role': request.args.get('role', default=0, type=int),
            'sortorder': Admin.check_sortorder()
        }

        if all(v is not None for v in [params['domain'], params['range'], params['prop']]):
            Admin.add_link(params)
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
    category = request.form.get('category', '')
    form_data = {
        'category': category,
        'acronym': request.form.get('acronym', ''),
        'email': request.form.get('email', ''),
        'website': request.form.get('website', ''),
        'orcid_id': request.form.get('orcid_id', ''),
        'image': request.form.get('image', ''),
        'case_study': request.form.get('case_study', type=int),
        'license_id': request.form.get('license_id', type=int)
    }

    # Add multi-language fields
    for col in ['name', 'address', 'description']:
        for lang_code in g.available_languages.keys():
            lang_key = f"{col}_{lang_code}"
            if lang_key in request.form:
                form_data[lang_key] = request.form.get(lang_key, '')

        # Also keep the default key for backward compatibility or display
        if col in request.form:
            form_data[col] = request.form.get(col, '')

    current_tab = f'nav-{category}'
    redirect_base = url_for('admin') + current_tab
    try:
        new_id = Admin.add_entry(form_data)
        flash(_('Entry added successfully!'), 'success')
        return redirect(f"{redirect_base}/{current_tab}{new_id}")
    except Admin.TooManyMainProjects:
        flash(
            _('Error adding entry %(name)s: Only one main project allowed',
              name=form_data["name"]),
            'danger')
    except Exception as e:
        flash(_(
            'Error adding entry %(name)s: %(error)s',
            name=form_data["name"],
            error=e), 'danger')
    return redirect(redirect_base)


@app.route('/admin/delete_entry/<int:id_>/<tab>')
@login_required
def delete_entry(id_: int, tab: str) -> Response:
    check_manager_user()
    if Admin.get_config_class_by_id(id_) == 5:
        flash(_('Main Project cannot be deleted'), 'danger')
        return redirect(url_for('admin', tab=tab))
    Admin.delete_entry(id_)
    flash(_('Entry deleted successfully!'), 'success')
    return redirect(url_for('admin', tab=tab))


@app.route('/edit_entry', methods=['POST', 'GET'])
@login_required
def edit_entry() -> Response:
    check_manager_user()

    config_id = request.form.get('config_id', type=int)
    if config_id is None:
        flash(_('Configuration ID is required'), 'danger')
        return _redirect_to_admin_tab('sidebar-projects-content')

    form_data = {
        'config_id': config_id,
        'acronym': request.form.get('acronym', ''),
        'email': request.form.get('email', ''),
        'website': request.form.get('website', ''),
        'orcid_id': request.form.get('orcid_id', ''),
        'image': request.form.get('image', ''),
        'case_study': request.form.get('case_study', type=int),
        'license_id': request.form.get('license_id', type=int)
    }

    # Add multi-language fields
    for col in ['name', 'address', 'description']:
        for lang_code in g.available_languages.keys():
            lang_key = f"{col}_{lang_code}"
            if lang_key in request.form:
                form_data[lang_key] = request.form.get(lang_key, '')

        # Also keep the default key for backward compatibility or display
        if col in request.form:
            form_data[col] = request.form.get(col, '')

    name = form_data.get('name', '')
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
            tab=request.form.get('current_tab'),
            _external=False))


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
        return _redirect_to_admin_tab('sidebar-maps')

    try:
        map_id = int(raw_map_id)
        if not check_if_map_id_exist(map_id):
            flash(_(f'Map with ID {map_id} not found'), 'danger')
            return _redirect_to_admin_tab('sidebar-maps')

        form_data: dict[str, str] = {
            'name': name,
            'display_name': display_name,
            'sort_order': sort_order,
            'tilestring': tile_string,
            'map_id': str(map_id)}

        Admin.update_map(form_data)
        flash(_('Map updated successfully'), 'success')

    except ValueError:
        flash(_('Invalid Map ID format'), 'danger')
    except Exception as e:
        app.logger.error("Map update failed: %s", e)
        flash(_('Error updating map: %(error)s', error=str(e)), 'danger')

    return _redirect_to_admin_tab('sidebar-maps')


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
        return _redirect_to_admin_tab('sidebar-maps')

    data: dict[str, str] = {
        'name': name,
        'display_name': display_name,
        'sort_order': sort_order,
        'tile_string': tile_string}
    try:
        map_id = Admin.add_new_map(data)
        flash(
            _('Map %(name)s with ID %(id)s added successfully!',
              name=data['name'], id=map_id),
            'success')
    except Exception as e:
        app.logger.error("Failed to add map: %s", e)
        flash(_(
            'Error adding map %(name)s: %(error)s', name=data['name'],
            error=e), 'danger')

    return _redirect_to_admin_tab('sidebar-maps')


@app.route('/admin/delete_map/<int:map_id>')
@login_required
def delete_map(map_id: int) -> Response:
    check_manager_user()
    try:
        Admin.delete_map(map_id)
        flash(_('Map deleted successfully!'), 'success')
    except Exception as e:
        flash(_('Error deleting map: %(error)s', error=str(e)), 'danger')
    return _redirect_to_admin_tab('sidebar-maps')


@app.route('/admin/choose_index_background', methods=['POST'])
@login_required
def choose_index_background() -> Response:
    check_manager_user()
    g.settings.index_map = request.form.get('mapselection', '')
    g.settings.index_img = request.form.get('default_img', '')
    g.settings.img_map = request.form.get('imgmap', '')
    g.settings.greyscale = request.form.get('greyscale') == 'on'
    try:
        g.settings.save_to_db()
        flash(_('Index background updated successfully'), 'success')
    except Exception as e:
        app.logger.error("Failed to set index background: %s", e)
        flash(_('Error updating settings'), 'error')

    return _redirect_to_admin_tab('sidebar-index-page-options')


@app.route('/admin/update_class_visibility', methods=['POST'])
@login_required
def update_class_visibility() -> Response:
    check_manager_user()
    g.settings.shown_classes = request.form.getlist('shown_classes')
    g.settings.hidden_classes = request.form.getlist('hidden_classes')

    def parse_ids(name: str) -> list[int]:
        raw = request.form.get(name, '')
        if not raw:
            return []
        res = []
        for x in raw.split(','):
            val = x.strip()
            if val:
                if not val.isdigit():
                    raise ValueError(val)
                res.append(int(val))
        return res

    try:
        g.settings.shown_types = parse_ids('shown_types')
        g.settings.hidden_types = parse_ids('hidden_types')
        g.settings.shown_ids = parse_ids('shown_ids')
        g.settings.hidden_ids = parse_ids('hidden_ids')
    except ValueError:
        flash(_('Invalid ID format. Please use comma-separated integers.'),
              'danger')
        return _redirect_to_admin_tab('sidebar-visibility-settings')

    g.settings.save_to_db()
    flash(_('Class visibility updated successfully.'), 'success')
    return _redirect_to_admin_tab('sidebar-visibility-settings')


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


@app.route('/admin/update_general_settings', methods=['POST'])
@app.route('/admin/update_general_settings/<int:ignore_id>', methods=['POST'])
@login_required
def update_general_settings(ignore_id: Optional[int] = None) -> Response:
    check_manager_user()
    case_study_id = int(request.form.get('case_study_id'))
    validation_result = Admin.check_case_study_type_id(case_study_id)
    if validation_result['is_valid']:
        g.settings.case_study_type_id = case_study_id
        g.settings.darkmode = request.form.get('darkMode') == 'on'
        g.settings.access_restriction = request.form.get(
            'accessRestriction') == 'on'
        g.settings.language_selector = request.form.get(
            'languageSelection') == 'on'
        g.settings.selected_languages = request.form.getlist(
            'selectedLanguages')
        g.settings.preferred_language = request.form.get(
            'preferredLanguage')
        g.settings.save_to_db()
        flash(_('Updated case study ID successfully'), 'info')
    else:
        message = _(
            'Invalid Case Study ID. Must be a positive integer '
            'and its entity type must be "type".')
        flash(message, 'error')
    return _redirect_to_admin_tab('sidebar-general-settings-group')


@app.route('/admin/check_case_study_id_ajax/<int:entity_id>', methods=['GET'])
@login_required
def check_case_study_id_ajax(entity_id: int) -> Response:
    check_manager_user()
    result = Admin.check_case_study_type_id(entity_id)
    return jsonify(result)


# Todo: remove for production
@app.route('/reset')
@login_required
def reset() -> Response:
    check_manager_user()
    if not current_app.config.get('DEBUG') and not current_app.config.get('TESTING'):
        flash(_('Reset is only allowed in debug or testing mode.'), 'danger')
        return redirect(url_for('admin'))
    make_reset()
    flash(_('reset database'), 'info')
    return redirect(url_for('admin'))


def make_reset() -> None:
    if not current_app.config.get('DEBUG') and not current_app.config.get('TESTING'):
        app.logger.warning('Attempted to reset database outside of DEBUG/TESTING mode.')
        return
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
    return _redirect_to_admin_tab('sidebar-cache-options')


@app.route("/admin/warm-entity-cache")
@login_required
def warm_entity_cache() -> Response:
    trigger_cache_warmup(False)
    flash(_("Cache warmup started in background (refresh mode)"), 'success')
    return _redirect_to_admin_tab('sidebar-cache-options')


@app.route("/admin/refresh-entity-cache")
@login_required
def refresh_entity_cache() -> Response:
    trigger_cache_warmup(True)
    flash(_("Cache warmup started in background."), 'success')
    return _redirect_to_admin_tab('sidebar-cache-options')


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
        flash(_("Error warming cache: %(error)s", error=str(e)), "error")
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
    return _redirect_to_admin_tab('sidebar-cache-options')


@app.route('/uploads/logos/<filename>')
def uploaded_logo(filename):
    return send_from_directory(
        os.path.join(app.root_path, '..', 'uploads', 'logos'), filename)


@app.route('/uploads/assets/<filename>')
def uploaded_asset(filename):
    return send_from_directory(
        os.path.join(app.root_path, '..', 'uploads', 'assets'), filename)


@app.context_processor
def utility_processor():
    def get_icon_url(filename):
        uploads_path = os.path.join(app.root_path, '..', 'uploads', 'icons')
        if os.path.exists(os.path.join(uploads_path, filename)):
            return url_for('uploaded_icon', filename=filename)
        return url_for('static', filename=f'images/icons/{filename}')

    return dict(get_icon_url=get_icon_url)


@app.route('/admin/upload_asset', methods=['POST'])
@login_required
def upload_asset():
    check_manager_user()
    if 'asset_file' not in request.files:
        flash(_('No file part'), 'danger')
        return _redirect_to_admin_tab('sidebar-assets')

    file = request.files['asset_file']
    if file.filename == '':
        flash(_('No selected file'), 'danger')
        return _redirect_to_admin_tab('sidebar-assets')

    if file:
        filename = secure_filename(file.filename)
        upload_path = os.path.join(app.root_path, '..', 'uploads', 'assets')
        os.makedirs(upload_path, exist_ok=True)
        file.save(os.path.join(upload_path, filename))
        add_asset_to_db(filename, is_default=False)
        flash(_('Asset "%(name)s" uploaded successfully.', name=filename),
              'success')

    return _redirect_to_admin_tab('sidebar-assets')


@app.route('/admin/rename_asset', methods=['POST'])
@login_required
def rename_asset():
    check_manager_user()
    old_name = request.form.get('old_name')
    new_name = request.form.get('new_name')

    if not old_name or not new_name:
        flash(_('Invalid request for renaming.'), 'danger')
        return _redirect_to_admin_tab('sidebar-assets')

    static_path = os.path.join(app.static_folder, 'assets')
    uploads_path = os.path.join(app.root_path, '..', 'uploads', 'assets')

    old_filepath_static = os.path.join(static_path, secure_filename(old_name))
    old_filepath_uploads = os.path.join(
        uploads_path, secure_filename(old_name))

    if os.path.exists(old_filepath_static):
        flash(_('Cannot rename default assets.'), 'danger')
        return _redirect_to_admin_tab('sidebar-assets')
    elif os.path.exists(old_filepath_uploads):
        old_filepath = old_filepath_uploads
        new_filepath = os.path.join(uploads_path, secure_filename(new_name))
    else:
        flash(_('Original file not found.'), 'danger')
        return _redirect_to_admin_tab('sidebar-assets')

    if os.path.exists(new_filepath):
        flash(_('A file with the new name already exists.'), 'danger')
        return _redirect_to_admin_tab('sidebar-assets')

    try:
        os.rename(old_filepath, new_filepath)
        rename_asset_in_db(old_name, new_name)
        flash(_('Asset renamed from "%(old)s" to "%(new)s".', old=old_name,
                new=new_name), 'success')
    except OSError as e:
        flash(_('Error renaming file: %(error)s', error=e), 'danger')

    return _redirect_to_admin_tab('sidebar-assets')


@app.route('/admin/delete_asset', methods=['POST'])
@login_required
def delete_asset():
    check_manager_user()
    filename = request.form.get('filename')
    if not filename:
        flash(_('No filename specified for deletion.'), 'danger')
        return _redirect_to_admin_tab('sidebar-assets')

    uploads_path = os.path.join(app.root_path, '..', 'uploads', 'assets')
    filepath_uploads = os.path.join(uploads_path, secure_filename(filename))

    if os.path.exists(filepath_uploads):
        try:
            os.remove(filepath_uploads)
            delete_asset_from_db(filename)
            flash(_('Asset "%(name)s" deleted successfully.', name=filename),
                  'success')
        except OSError as e:
            flash(_('Error deleting file: %(error)s', error=e), 'danger')
    else:
        delete_asset_from_db(filename)
        flash(_('Default asset "%(name)s" deactivated.', name=filename), 'success')

    return _redirect_to_admin_tab('sidebar-assets')


@app.route('/admin/update_asset_license', methods=['POST'])
@login_required
def update_asset_license() -> Response:
    check_manager_user()

    filename = request.form.get('filename', '')
    license_id = request.form.get('license_id', type=int)
    attribution = request.form.get('attribution', '')

    admin_instance = Admin()
    admin_instance.update_file_license(filename, license_id, attribution)

    flash(_('Asset license updated successfully.'), 'success')
    return _redirect_to_admin_tab('sidebar-assets')




@app.route('/uploads/team/<filename>')
def uploaded_team(filename):
    return send_from_directory(
        os.path.join(app.root_path, '..', 'uploads', 'team'), filename)


@app.route('/uploads/icons/<filename>')
def uploaded_icon(filename):
    return send_from_directory(
        os.path.join(app.root_path, '..', 'uploads', 'icons'), filename)


@app.route('/uploads/favicon.ico')
def uploaded_favicon():
    return send_from_directory(
        os.path.join(app.root_path, '..', 'uploads'), 'favicon.ico')


@app.route('/admin/upload_file', methods=['POST'])
@login_required
def upload_file():
    check_manager_user()
    file_type = request.form.get('file_type')
    if not file_type:
        flash(_('File type is missing.'), 'danger')
        return _redirect_to_admin_tab('sidebar-file-management-group')

    if 'file' not in request.files:
        flash(_('No file part'), 'danger')
        return _redirect_to_admin_tab(f'sidebar-{file_type}')

    file = request.files['file']
    if file.filename == '':
        flash(_('No selected file'), 'danger')
        return _redirect_to_admin_tab(f'sidebar-{file_type}')

    if file:
        filename = secure_filename(file.filename)
        if file_type == 'logo':
            upload_folder = 'logos'
        elif file_type == 'asset':
            upload_folder = 'assets'
        elif file_type == 'team':
            upload_folder = 'team'
        elif file_type == 'icon':
            upload_folder = 'icons'
        else:
            flash(_('Invalid file type.'), 'danger')
            return _redirect_to_admin_tab('sidebar-file-management-group')

        upload_path = os.path.join(app.root_path, '..', 'uploads', upload_folder)
        os.makedirs(upload_path, exist_ok=True)
        file.save(os.path.join(upload_path, filename))
        add_file_to_db(filename, file_type, is_default=False)
        flash(_('%(type)s "%(name)s" uploaded successfully.', type=file_type.capitalize(), name=filename), 'success')

    return _redirect_to_admin_tab(f'sidebar-{file_type}-management')


@app.route('/admin/rename_file', methods=['POST'])
@login_required
def rename_file():
    check_manager_user()
    old_name = request.form.get('old_name')
    new_name = request.form.get('new_name')
    file_type = request.form.get('file_type')

    if not all([old_name, new_name, file_type]):
        flash(_('Invalid request for renaming.'), 'danger')
        return _redirect_to_admin_tab('sidebar-file-management-group')

    if file_type == 'logo':
        upload_folder = 'logos'
        static_folder = 'images/logos'
    elif file_type == 'asset':
        upload_folder = 'assets'
        static_folder = 'assets'
    elif file_type == 'team':
        upload_folder = 'team'
        static_folder = 'images/team'
    else:
        flash(_('Invalid file type.'), 'danger')
        return _redirect_to_admin_tab('sidebar-file-management-group')

    static_path = os.path.join(app.static_folder, static_folder)
    uploads_path = os.path.join(app.root_path, '..', 'uploads', upload_folder)

    old_filepath_static = os.path.join(static_path, secure_filename(old_name))
    old_filepath_uploads = os.path.join(
        uploads_path, secure_filename(old_name))

    if os.path.exists(old_filepath_static):
        flash(_('Cannot rename default files.'), 'danger')
        return _redirect_to_admin_tab(f'sidebar-{file_type}-management')
    elif os.path.exists(old_filepath_uploads):
        old_filepath = old_filepath_uploads
        new_filepath = os.path.join(uploads_path, secure_filename(new_name))
    else:
        flash(_('Original file not found.'), 'danger')
        return _redirect_to_admin_tab(f'sidebar-{file_type}-management')

    if os.path.exists(new_filepath):
        flash(_('A file with the new name already exists.'), 'danger')
        return _redirect_to_admin_tab(f'sidebar-{file_type}-management')

    try:
        os.rename(old_filepath, new_filepath)
        rename_file_in_db(old_name, new_name, file_type)
        flash(_('%(type)s renamed from "%(old)s" to "%(new)s".', type=file_type.capitalize(), old=old_name, new=new_name), 'success')
    except OSError as e:
        flash(_('Error renaming file: %(error)s', error=e), 'danger')

    return _redirect_to_admin_tab(f'sidebar-{file_type}-management')


@app.route('/admin/delete_file', methods=['POST'])
@login_required
def delete_file():
    check_manager_user()
    filename = request.form.get('filename')
    file_type = request.form.get('file_type')

    if not filename or not file_type:
        flash(_('No filename or type specified for deletion.'), 'danger')
        return _redirect_to_admin_tab('sidebar-file-management-group')

    if file_type == 'logo':
        upload_folder = 'logos'
    elif file_type == 'asset':
        upload_folder = 'assets'
    elif file_type == 'team':
        upload_folder = 'team'
    elif file_type == 'icon':
        upload_folder = 'icons'
    else:
        flash(_('Invalid file type.'), 'danger')
        return _redirect_to_admin_tab('sidebar-file-management-group')

    uploads_path = os.path.join(app.root_path, '..', 'uploads', upload_folder)
    filepath_uploads = os.path.join(uploads_path, secure_filename(filename))

    if os.path.exists(filepath_uploads):
        try:
            os.remove(filepath_uploads)
            delete_file_from_db(filename, file_type)
            flash(_('%(type)s "%(name)s" deleted successfully.', type=file_type.capitalize(), name=filename), 'success')
        except OSError as e:
            flash(_('Error deleting file: %(error)s', error=e), 'danger')
    else:
        delete_file_from_db(filename, file_type)
        flash(_('Default %(type)s "%(name)s" deactivated.', type=file_type.capitalize(), name=filename), 'success')

    return _redirect_to_admin_tab(f'sidebar-{file_type}-management')


@app.route('/admin/update_file_license', methods=['POST'])
@login_required
def update_file_license() -> Response:
    check_manager_user()

    filename = request.form.get('filename', '')
    file_type = request.form.get('file_type', '')
    license_id = request.form.get('license_id', type=int)
    attribution = request.form.get('attribution', '')

    admin_instance = Admin()
    admin_instance.update_file_license(filename, license_id, attribution)

    flash(_('%(type)s license updated successfully.', type=file_type.capitalize()), 'success')
    return _redirect_to_admin_tab(f'sidebar-{file_type}-management')
