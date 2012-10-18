from flask import current_app

def localize_datetime(value):
    # Return immediatley if a naive datetime is received
    if not value.tzinfo:
        return value

    time_zone = current_app.config['TIME_ZONE']
    return time_zone.normalize(value.astimezone(time_zone))

def format_datetime(value, format_string=None):
    if not format_string:
        format_string = current_app.config['DATETIME_FORMAT']
    return value.strftime(format_string)

def register_all(app):
    app.add_template_filter(localize_datetime)
    app.add_template_filter(format_datetime)
