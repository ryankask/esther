from flask import Blueprint, current_app, request, abort, url_for
from flask.ext.login import current_user
from sqlalchemy.orm import contains_eager

from esther import db
from esther.forms import ListForm, ItemForm
from esther.json import dumps
from esther.models import prep_query_for_json, User, List, Item

blueprint = Blueprint('todo', __name__)

API_EMPTY_BODY_ERROR = {'__all__': [u'Request body must contain data.']}
API_INVALID_PARAMETERS = {'__all__': [u'Invalid parameters in request body.']}

def json_response(data, status=200, headers=None):
    return current_app.response_class(dumps(data), status,
                                      mimetype='application/json',
                                      headers=headers or {})

def stripped_form(form_class, form_data, obj):
    """
    Create a form suitable for PATCH requests. Any form fields that aren't
    in the PATCH data dict are removed from the form instance.

    If the request contains parameters not found on the form, ``None`` is
    returned.
    """
    form = form_class(form_data, obj=obj)
    form_fields = [field.name for field in form]

    if not set(form_data.keys()).issubset(set(form_fields)):
        return None

    for field_name in form_fields:
        if field_name not in form_data:
            delattr(form, field_name)

    return form

def patch(obj, form_class, owner, is_public):
    if owner != current_user:
        if not is_public:
            abort(404)
        else:
            abort(403)

    if not request.form:
        return json_response(API_EMPTY_BODY_ERROR, 400)

    form = stripped_form(form_class, request.form, obj)
    if not form:
        return json_response(API_INVALID_PARAMETERS, 400)

    if form.validate():
        form.populate_obj(obj)
        db.session.commit()
        return json_response(obj.as_dict())
    else:
        return json_response(form.errors, 422)


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
            headers = {'location': url_for('.list_detail', owner_id=owner.id,
                                           slug=new_list.slug)}
            return u'', 201, headers
        return json_response(form.errors, 422)

    todo_lists = List.query.order_by(List.created).filter(List.owner == owner)
    if owner != current_user:
        todo_lists = todo_lists.filter(List.is_public == True)
    prepped_todo_lists = prep_query_for_json(todo_lists)
    return json_response(prepped_todo_lists)

@blueprint.route('/api/<int:owner_id>/lists/<slug>', methods=('GET', 'PATCH'))
def list_detail(owner_id, slug):
    todo_list = List.query.filter_by(owner_id=owner_id, slug=slug).first_or_404()

    if request.method == 'PATCH':
        return patch(todo_list, ListForm, todo_list.owner, todo_list.is_public)

    if not todo_list.is_public and todo_list.owner != current_user:
        abort(404)
    return json_response(todo_list.as_dict())

@blueprint.route('/api/<int:owner_id>/lists/<list_slug>/items',
                 methods=('GET', 'POST'))
def items(owner_id, list_slug):
    query = List.query.filter_by(owner_id=owner_id, slug=list_slug)
    todo_list = query.first_or_404()

    if not todo_list.is_public and todo_list.owner != current_user:
        abort(404)

    if request.method == 'POST':
        if todo_list.owner != current_user:
            abort(403)
        form = ItemForm(request.form)
        if form.validate_on_submit():
            item = Item(todo_list=todo_list)
            form.populate_obj(item)
            db.session.add(item)
            db.session.commit()
            location = url_for('.item_detail', owner_id=current_user.id,
                               list_slug=item.todo_list.slug, item_id=item.id)
            return u'', 201, {'location': location}
        return json_response(form.errors, 422)

    prepped_items = prep_query_for_json(todo_list.items)
    return json_response(prepped_items)

@blueprint.route('/api/<int:owner_id>/lists/<list_slug>/items/<int:item_id>',
                 methods=('GET', 'PATCH'))
def item_detail(owner_id, list_slug, item_id):
    item = Item.query.options(contains_eager('todo_list')).join(List).filter(
        Item.id == item_id,
        List.slug == list_slug,
        List.owner_id == owner_id).first_or_404()
    todo_list = item.todo_list

    if request.method == 'PATCH':
        return patch(item, ItemForm, todo_list.owner, todo_list.is_public)

    if not todo_list.is_public and todo_list.owner != current_user:
        abort(404)
    return json_response(item.as_dict())
