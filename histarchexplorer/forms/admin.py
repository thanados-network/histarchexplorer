from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, HiddenField
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
