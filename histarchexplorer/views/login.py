# Created by Alexander Watzinger and others.
# Please see README.md for licensing information

from bcrypt import hashpw
from flask import flash, render_template, request, url_for, abort
from flask_login import (
    LoginManager, current_user, login_required, login_user, logout_user)
from flask_wtf import FlaskForm
from werkzeug import Response
from werkzeug.utils import redirect
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import InputRequired

from histarchexplorer import app
from histarchexplorer.models.user import UserMapper

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id: int) -> UserMapper:
    return UserMapper.get_by_id(user_id)


class LoginForm(FlaskForm):
    username = StringField(
        'Username', [InputRequired()],
        render_kw={'autofocus': True})
    password = PasswordField('Password', [InputRequired()])
    show_passwords = BooleanField('show password')
    save = SubmitField('login')


@app.route('/login', methods=["GET", "POST"])
def login() -> str | Response:
    if current_user.is_authenticated:
        return redirect('/')
    form = LoginForm()
    if form.validate_on_submit():
        user = UserMapper.get_by_username(request.form['username'])
        if user:
            hash_ = hashpw(
                request.form['password'].encode('utf-8'),
                user.password.encode('utf-8'))
            if hash_ == user.password.encode('utf-8'):
                if user.active:
                    login_user(user)
                    return redirect(
                        request.args.get('next') or url_for('index'))
                else:  # pragma: no cover
                    flash('error inactive', 'error')
            else:  # pragma: no cover
                flash('error wrong password', 'error')
        else:
            flash('error username', 'error')
    error_html = ''
    if form and hasattr(form, 'errors'):
        for field_name, error_messages in form.errors.items():
            error_html += field_name + ' - ' + error_messages[0] + '<br />'
    return render_template('login.html', form=form, error_html=error_html)


@app.route('/logout')
@login_required
def logout() -> Response:
    logout_user()
    return redirect('/')


