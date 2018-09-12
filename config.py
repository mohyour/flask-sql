import os


class Config(object):
    DEBUG = False
    database = os.getenv('database')
    user = os.getenv('user')


class Development(Config):
    DEBUG = True
