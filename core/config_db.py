import os


class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv("SQLALCHEMY_TRACK_MODIFICATIONS")


class DevelopmentConfig(Config):
    """
    Development configurations
    """
    DEBUG = os.getenv('DEV_DEBUG')
    DATABASE = os.getenv('DEV_DB_NAME')
    USER = os.getenv('DEV_DB_USER')
    PASSWORD = os.getenv('DEV_DB_PASSWORD')
    HOST = os.getenv('DEV_DB_HOST')
    COLLECTION = os.getenv('DEV_COLLECTION')
    DB_STRING = f'mongodb+srv://{USER}:{PASSWORD}@{HOST}/{DATABASE}?retryWrites=true&w=majority'


class ProductionConfig(Config):
    """
    Production configurations
    """
    DEBUG = os.getenv('PROD_DEBUG')
    DATABASE = os.getenv('PROD_DB_NAME')
    USER = os.getenv('PROD_DB_USER')
    PASSWORD = os.getenv('PROD_DB_PASSWORD')
    HOST = os.getenv('PROD_DB_HOST')
    COLLECTION = os.getenv('PROD_COLLECTION')
    DB_STRING = f'mongodb+srv://{USER}:{PASSWORD}@{HOST}/{DATABASE}?retryWrites=true&w=majority'


