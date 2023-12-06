# -*- coding: utf-8 -*-
"""The __init__.py file - Application Factory.
This file's task is to initialize the app multiple times, especially for testing.
"""

import os
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_pagedown import PageDown
from flask_login import LoginManager
from config import config

login_manager = LoginManager()
login_manager.login_view = 'auth.login'

bootstrap = Bootstrap()
moment = Moment()
db = SQLAlchemy()
mail = Mail()


def safe_url(target):
    return target.startswith('/') or target.startswith('http://')


# Initializing the app components
def initialize_app(app):
    mail.init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    pagedown = PageDown(app)


def create_app(config_name):
    app = Flask(__name__)

    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    initialize_app(app)

    # MAIN BLUEPRINT
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    # Authentication BLUEPRINT
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint,url_prefix='/api/v1/')

    return app
