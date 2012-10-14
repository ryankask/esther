from flask import Flask, render_template
from flask.ext.bcrypt import Bcrypt
from flask.ext.login import LoginManager
from flask.ext.mail import Mail
from flask.ext.sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()
mail = Mail()
login_manager = LoginManager()

def create_app(config_objects):
    app = Flask(__name__)

    for config_object in config_objects:
        app.config.from_object(config_object)

    bcrypt.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    from esther import models
    from esther.views import auth
    from esther.views import blog
    from esther.views import general

    app.register_blueprint(auth.blueprint)
    app.register_blueprint(blog.blueprint, url_prefix='/blog')
    app.register_blueprint(general.blueprint)

    # Flask-Login settings are stored on the ``LoginManager`` instance
    auth.configure(login_manager, app)

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('errors/500.html'), 500

    return app
