from flask import Flask, render_template
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.bcrypt import Bcrypt

bcrypt = Bcrypt()
db = SQLAlchemy()

def create_app(config_objects):
    app = Flask(__name__)

    for config_object in config_objects:
        app.config.from_object(config_object)

    bcrypt.init_app(app)
    db.init_app(app)

    from esther import models
    from esther.views import general

    app.register_blueprint(general.blueprint)

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('errors/500.html'), 500

    return app
