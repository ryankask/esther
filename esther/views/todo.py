from flask import Blueprint, current_app
from flask.ext.login import current_user

from esther.json import dumps
from esther.models import prep_query_for_json, User, List

blueprint = Blueprint('todo', __name__)

def json_response(data, status=200, headers=None):
    return current_app.response_class(dumps(data), status,
                                      mimetype='application/json',
                                      headers=headers or {})

@blueprint.route('/api/<int:owner_id>/lists', methods=['GET'])
def lists(owner_id):
    owner = User.query.get_or_404(owner_id)
    todo_lists = List.query.order_by(List.created).filter(List.owner == owner)
    if not current_user.is_authenticated() or owner != current_user:
        todo_lists = todo_lists.filter(List.is_public == True)
    prepped_todo_lists = prep_query_for_json(todo_lists)
    return json_response(prepped_todo_lists)
