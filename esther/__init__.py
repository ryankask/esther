from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('esther.settings.site')
db = SQLAlchemy(app)

from esther import models
from esther.views import general
