from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import (
    StringField, IntegerField, TextAreaField, HiddenField, BooleanField,
    SelectField, SelectMultipleField)
from wtforms.validators import DataRequired, Optional
from flask_babel import gettext as _


class MapForm(FlaskForm):
    map_id = HiddenField('Map ID')
    name = StringField(_('name'), validators=[DataRequired()])
    displayname = StringField(_('Display Name'), validators=[DataRequired()])
    inputorder = IntegerField(_('order'), validators=[Optional()], default=0)
    description = TextAreaField(
        _('Leaflet Tile Layer String'),
        validators=[DataRequired()])


class GeneralSettingsForm(FlaskForm):
    case_study_id = IntegerField(
        _('case study hierarchy ID'),
        validators=[DataRequired()])
    darkMode = BooleanField(_('Deactivate Darkmode'))
    languageSelection = BooleanField(_('Deactivate Language Selector'))
    accessRestriction = BooleanField(_('Activate Access Restriction'))
    selectedLanguages = SelectMultipleField(_('available languages'))
    preferredLanguage = SelectField(_('preferred language'))


class LicenseForm(FlaskForm):
    spdx_id = StringField(_('SPDX ID'), validators=[DataRequired()])
    uri = StringField(_('URI'), validators=[DataRequired()])
    label = StringField(_('Label'), validators=[DataRequired()])
    category = SelectField(
        _('Category'),
        choices=[('LICENSE', 'LICENSE'), ('STATEMENT', 'STATEMENT')],
        validators=[DataRequired()])


class FileUploadForm(FlaskForm):
    file = FileField(_('file'), validators=[FileRequired()])
    file_type = HiddenField('file_type')
    active_sidebar = HiddenField('active_sidebar')


class FileLicenseForm(FlaskForm):
    filename = HiddenField('filename')
    file_type = HiddenField('file_type')
    active_sidebar = HiddenField('active_sidebar')
    license_id = SelectField(
        _('License'),
        coerce=int,
        validators=[Optional()])
    attribution = StringField(_('Attribution'), validators=[Optional()])


class FileRenameForm(FlaskForm):
    old_name = HiddenField('old_name')
    new_name = StringField(_('New Name'), validators=[DataRequired()])
    file_type = HiddenField('file_type')
    active_sidebar = HiddenField('active_sidebar')


class FileDeleteForm(FlaskForm):
    filename = HiddenField('filename')
    file_type = HiddenField('file_type')
    active_sidebar = HiddenField('active_sidebar')
