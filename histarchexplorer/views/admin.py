from flask import render_template, abort
from flask_login import (
    LoginManager, current_user, login_required)

from histarchexplorer import app

@app.route('/admin')
@login_required
def admin() -> str:
    if current_user.group not in ['admin', 'manager']:
        abort(403)



    return render_template("/admin.html")
