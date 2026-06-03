from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import InputRequired
from flask_babel import gettext as _


class LoginForm(FlaskForm):
    username = StringField(
        _('username'),
        [InputRequired()],
        render_kw={'autofocus': True})
    password = PasswordField(_('password'), [InputRequired()])
    show_passwords = BooleanField(_('show password'))
    save = SubmitField(_('login'))
