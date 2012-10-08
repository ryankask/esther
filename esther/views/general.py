from flask import render_template

from esther import app

@app.route('/')
def index():
    return render_template('general/index.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('errors/500.html'), 500
