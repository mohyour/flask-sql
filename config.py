import os


class Config(object):
    DEBUG = False
    CSRF_ENABLED = True
    SECRET_KEY = os.getenv('secret_key')
    database = os.getenv('database')
    user = os.getenv('user')


class Development(Config):
    DEBUG = True
