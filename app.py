from flask import Flask
import os
from dotenv import load_dotenv
from flask_pymongo import pymongo, PyMongo
from core.config_db import ProductionConfig, DevelopmentConfig, Config

app = Flask(__name__, template_folder='templates')
load_dotenv()
app.secret_key = os.getenv("SECRET_KEY")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = Config.SQLALCHEMY_TRACK_MODIFICATIONS

if os.getenv('ENVIRONMENT') == 'prod':
    config = ProductionConfig()
else:
    config = DevelopmentConfig()

app.config["MONGO_URI"] = config.DB_STRING
mongo = PyMongo(app)
ads_collection = pymongo.collection.Collection(mongo.db, config.COLLECTION)


from urls import *
# from .models import *
