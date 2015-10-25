import os
from datetime import timedelta


basedir = os.path.abspath(os.path.dirname(__file__))

class BaseConfig:
    """ Defines base configurations that are common across all deploys
    """
    
    SECRET_KEY = os.environ.get('BUCKETLIST_SECRET_KEY') or 'NotSoSecretNowIsIt?'
    
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    DATE_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

    JWT_AUTH_USERNAME_KEY = 'email'
    JWT_AUTH_PASSWORD_KEY = 'password'
    JWT_EXPIRATION_DELTA = timedelta(hours=1)
    JWT_AUTH_URL_RULE = '/api/v1.0/auth/login'
    JWT_AUTH_URL_OPTIONS = {
        'endpoint': 'login',
        'methods': ['POST']
    }

    @staticmethod
    def init_app(app):
        # Any config level initialization can be done here, not needed for now!
        pass
        
        
class DevelopmentConfig(BaseConfig):
    """ Defines configurations for development
    """
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('BUCKETLIST_DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'bucketlist-dev.sqlite')


class TestingConfig(BaseConfig):
    """ Defines configurations for testing
    """
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('BUCKETLIST_TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'bucketlist-test.sqlite')


class ProductionConfig(BaseConfig):
    """ Defines configurations for production
    """
    SQLALCHEMY_DATABASE_URI = os.environ.get('BUCKETLIST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'bucketlist.sqlite')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
