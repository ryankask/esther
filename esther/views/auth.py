from functools import wraps

from flask import (Blueprint, request, render_template, redirect, url_for,
                   flash, abort)
from flask.ext.login import (login_user, logout_user, login_required,
                             current_user)

from esther import db
from esther.forms import LoginForm, UserForm, AddUserForm
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

def admin_required(func):
    @wraps(func)
    @login_required
    def decorated(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return func(*args, **kwargs)
    return decorated

@blueprint.route('/users')
@admin_required
def list_users():
    users = User.query.order_by(User.email).all()
    return render_template('auth/user_list.html', users=users)

@blueprint.route('/users/add', methods=('GET', 'POST'))
@admin_required
def add_user():
    form = AddUserForm()

    if form.validate_on_submit():
        user = User(email=form.email.data, full_name=form.full_name.data,
                    short_name=form.short_name.data, password=form.password.data,
                    is_admin=form.is_admin.data)
        db.session.add(user)
        db.session.commit()

        message = u'User "{}" successfully added.'.format(user.email)
        flash(message, 'success')
        return redirect(url_for('.list_users'))

    return render_template('auth/user_add.html', form=form)

@blueprint.route('/users/<int:user_id>', methods=('GET', 'POST'))
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = UserForm(request.form, obj=user)

    if form.validate_on_submit():
        form.populate_obj(user)
        db.session.commit()

        message = u'Edited user "{}".'.format(user.email)
        flash(message, 'success')
        return redirect(url_for('.list_users'))

    return render_template('auth/user_edit.html', user=user, form=form)
