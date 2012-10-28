from flask import (Blueprint, request, render_template, redirect, url_for,
                   flash, abort)
from flask.ext.login import (login_user, logout_user, login_required,
                             current_user)

from esther.forms import LoginForm
from esther.models import User

blueprint = Blueprint('auth', __name__)

def configure(login_manager, app):
    login_manager.login_view = app.config.get('AUTH_LOGIN_VIEW', 'auth.login')
    login_manager.login_message = app.config.get('AUTH_LOGIN_MESSAGE', None)
    # Bind ``user_callback`` here instead of using the API's decorator
    login_manager.user_callback = load_user

def load_user(user_id):
    return User.query.get(user_id)

@blueprint.route('/login', methods=('GET', 'POST'))
def login():
    form = LoginForm()

    if form.validate_on_submit():
        login_user(form.user)
        return redirect(request.args.get('next') or url_for('general.index'))

    return render_template('auth/login.html', form=form)

@blueprint.route('/logout')
def logout():
    logout_user()
    flash(u'You have successfully logged out.', 'success')
    return redirect(request.args.get('next') or url_for('general.index'))

### User management views

@login_required
@blueprint.route('/users')
def list_users():
    if not current_user.is_admin:
        abort(403)
    users = User.query.order_by(User.email).all()
    return render_template('auth/user_list.html', users=users)
