from flask import Blueprint, current_app, request, abort, url_for
from flask.ext.login import current_user

from esther import db
from esther.forms import ListForm
from esther.json import dumps
from esther.models import prep_query_for_json, User, List

blueprint = Blueprint('todo', __name__)

def json_response(data, status=200, headers=None):
    return current_app.response_class(dumps(data), status,
                                      mimetype='application/json',
                                      headers=headers or {})

@blueprint.route('/api/<int:owner_id>/lists', methods=('GET', 'POST'))
def lists(owner_id):
    owner = User.query.get_or_404(owner_id)

    if request.method == 'POST':
        if owner != current_user:
            abort(403)
        form = ListForm(request.form)
        if form.validate_on_submit():
            new_list = List(owner=owner)
            form.populate_obj(new_list)
            db.session.add(new_list)
            db.session.commit()
            headers = {'location': url_for('.list_', owner_id=owner.id,
                                           slug=new_list.slug)}
            return u'', 201, headers
        return json_response(form.errors, 422)

    todo_lists = List.query.order_by(List.created).filter(List.owner == owner)
    if owner != current_user:
        todo_lists = todo_lists.filter(List.is_public == True)
    prepped_todo_lists = prep_query_for_json(todo_lists)
    return json_response(prepped_todo_lists)

@blueprint.route('/api/<int:owner_id>/lists/<slug>')
def list_(owner_id, slug):
    todo_list = List.query.filter_by(slug=slug).first_or_404()
    if not todo_list.is_public and todo_list.owner != current_user:
        abort(404)
    return json_response(todo_list.as_dict())
