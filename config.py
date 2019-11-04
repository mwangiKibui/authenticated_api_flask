import os
basedir = os.path.abspath(os.path.dirname(__file__))
DEBUG=True
SECRET_KEY='Thisisasecret!'
SQLALCHEMY_DATABASE_URI = 'sqlite:////' + os.path.join(basedir, 'db.sqlite')
SQLALCHEMY_TRACK_MODIFICATIONS=True