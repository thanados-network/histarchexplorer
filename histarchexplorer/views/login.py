from typing import Optional

from bcrypt import hashpw
from flask import flash, render_template, request, url_for
from flask_babel import gettext as _
from flask_login import (
    LoginManager, current_user, login_required, login_user, logout_user)
from werkzeug import Response
from werkzeug.utils import redirect

from histarchexplorer import app
from histarchexplorer.forms.login import LoginForm
from histarchexplorer.models.user import User


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id: int) -> Optional[User]:  # pragma: no cover
    return User.get_by_id(user_id)


@app.route('/login', methods=["GET", "POST"])
def login() -> str | Response:
    """Handle administrative user login.

    Validates login credentials, authenticates the user, and redirects
    to the admin dashboard or the requested next URL.
    """
    if current_user.is_authenticated:
        return redirect(url_for('admin'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_by_username(form.username.data)
        if user:
            hash_ = hashpw(
                form.password.data.encode('utf-8'),
                user.password.encode('utf-8'))
            if hash_ == user.password.encode('utf-8'):
                if user.active:
                    login_user(user)
                    return redirect(
                        request.args.get('next') or url_for('index'))
                flash(_('Your account is inactive.'), 'error')
            else:
                flash(_('Incorrect password.'), 'error')
        else:
            flash(_('User not found.'), 'error')
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout() -> Response:
    """Log out the current user and redirect to the landing page.

    Terminates the active user session.
    """
    logout_user()
    return redirect('/')
