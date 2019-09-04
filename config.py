import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
        # The Flask-WTF extension uses SECRET_KEY to protect web forms against CSRF attacks
        # When this application is deployed on a production server, set a unique and difficult to guess value in the
        # environment, so that the server has a secure key that nobody else knows.

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    DOGECOIN_REWARD = 1234
        # JMC I think this should be set to 50% of our reward pot

    DOGECOIN_PK = os.environ.get('DOGECOIN_PK') or 'a-test-private-key'
        # the private key of the reward pot, well it has to be stored somewhere [gulp]

    DOGECOIN_NODE_VERSION = '/Shibetoshi:1.14.0/'
        # the version string that we need people to upgrade to
