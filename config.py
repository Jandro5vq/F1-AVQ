class Config(object):
    TRAP_HTTP_EXCEPTIONS = True
    SCHEDULER_API_ENABLED = True
    SECRET_KEY = '6QUWcs*BZPcm&!@oT^tc'
    SESSION_COOKIE_NAME = 'AVQ F1 Session'
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'alejandro'
    MYSQL_PASSWORD = '5122000'
    MYSQL_DB = 'avqf1'

class DevelopmentConfig(Config):
    DEBUG = True

class PublicConfig(Config):
    DEBUG = False

conf = {
    'development': DevelopmentConfig,
    'public' : PublicConfig
}