from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

app = Flask(__name__)
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)
ma = Marshmallow(app)

from routes import *

if __name__ == '__main__':
    app.run()