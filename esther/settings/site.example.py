# Example ``esther.settings.site`` settings file
from esther.settings.base import *

# Change the secret key, of course
SECRET_KEY = '4=w9+w5+4gb%+u$-y)3@6ar5z+2j7k!lzkkouilnweea$f&lcw'
SQLALCHEMY_DATABASE_URI = 'postgresql://user:password@localhost:5432/esther'
DEBUG_TB_INTERCEPT_REDIRECTS = False

CONTACT_EMAIL_SENDER = u'webmaster@example.com'
CONTACT_EMAIL_RECIPIENTS = [u'me@example.com']

MAIL_SERVER = 'smtp.example.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = 'username'
MAIL_PASSWORD = 'password'

SENTRY_DSN = 'https://'
