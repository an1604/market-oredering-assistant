import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.googlemail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in \
                   ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'
    FLASKY_MAIL_SENDER = 'Flasky Admin <flasky@example.com>'
    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')
    SSL_REDIRECT = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True  # enable the slow query reporting on production
    FLASKY_POSTS_PER_PAGE = 20
    FLASKY_FOLLOWERS_PER_PAGE = 50
    FLASKY_COMMENTS_PER_PAGE = 30
    FLASKY_SLOW_DB_QUERY_TIME = 0.5

    # ML\DL Deployment
    TF_CPP_MIN_LOG_LEVEL = os.environ['TF_CPP_MIN_LOG_LEVEL']

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    FLASK_CONFIG = 'development'
    SQLALCHEMY_DATABASE_URI = os.environ['MySQL_connection_DEV']
    engine = create_engine(SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)


class TestingConfig(Config):
    FLASK_CONFIG = 'testing'
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = os.environ['MySQL_connection_TEST']
    engine = create_engine(SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)


class ProductionConfig(Config):
    FLASK_CONFIG = 'production'
    SQLALCHEMY_DATABASE_URI = os.environ['MySQL_connection_PRODUCTION']
    engine = create_engine(SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        # email errors to the administrators
        import logging
        from logging.handlers import SMTPHandler
        credentials = None
        secure = None
        if getattr(cls, 'MAIL_USERNAME', None) is not None:
            credentials = (cls.MAIL_USERNAME, cls.MAIL_PASSWORD)
            if getattr(cls, 'MAIL_USE_TLS', None):
                secure = ()
        mail_handler = SMTPHandler(
            mailhost=(cls.MAIL_SERVER, cls.MAIL_PORT),
            fromaddr=cls.FLASKY_MAIL_SENDER,
            toaddrs=[cls.FLASKY_ADMIN],
            subject=cls.FLASKY_MAIL_SUBJECT_PREFIX + ' Application Error',
            credentials=credentials,
            secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
