import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DOGECOIN_REWARD = 1234
    DOGECOIN_PK = 'set-this-value-later'
    DOGECOIN_NODE_VERSION = '/Shibetoshi:1.14.0/'

