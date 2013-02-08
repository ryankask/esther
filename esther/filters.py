from flask import current_app
from jinja2 import Markup
import markdown as md

def localize_datetime(value):
    # Return immediatley if a naive datetime is received
    if not value.tzinfo:
        return value

    time_zone = current_app.config['TIME_ZONE']
    return time_zone.normalize(value.astimezone(time_zone))

def format_datetime(value, format_string=None,
                    default_setting='DATETIME_FORMAT'):
    if not format_string:
        format_string = current_app.config[default_setting]
    return value.strftime(format_string)

def format_date(value, format_string=None):
    return format_datetime(value, format_string, 'DATE_FORMAT')

def markdown(value):
    return Markup(md.markdown(value, ['codehilite']))

def register_all(app):
    app.add_template_filter(localize_datetime)
    app.add_template_filter(format_datetime)
    app.add_template_filter(format_date)
    app.add_template_filter(markdown)
