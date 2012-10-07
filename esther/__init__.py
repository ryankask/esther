from flask import Flask

app = Flask(__name__)
app.config.from_object('esther.settings.site')

from esther.views import general
