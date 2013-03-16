from flask import Blueprint, render_template

blueprint = Blueprint('angular', __name__, template_folder='templates',
                      static_folder='static')

@blueprint.route('/runner')
def runner():
    return render_template('angular/runner.html')
