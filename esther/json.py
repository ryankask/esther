"""
Adapted from https://github.com/mitsuhiko/flask/blob/master/flask/json.py,
which will be included in Flask 0.10.
"""
from datetime import datetime
import simplejson as json

from werkzeug.http import http_date


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return http_date(o)
        return json.JSONEncoder.default(self, o)


def dumps(obj, **kwargs):
    kwargs.setdefault('cls', JSONEncoder)
    return json.dumps(obj, **kwargs)
