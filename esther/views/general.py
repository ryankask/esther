from flask import Blueprint, render_template

blueprint = Blueprint('general', __name__)

@blueprint.route('/')
def index():
    return render_template('general/index.html')

@blueprint.route('/about')
def about():
    return render_template('general/about.html')
