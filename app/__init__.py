from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask_restful import reqparse, abort, Api, Resource
from flask.ext.login import LoginManager

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
api = Api(app)
login_manager = LoginManager()
login_manager.init_app(app)

from app import views, models


@login_manager.user_loader
def load_user(user_id):
    return models.User.query.get(user_id)


