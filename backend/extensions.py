"""
This file contains Flask extensions instances that are used across the application.
Separating these instances helps avoid circular imports.
"""
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager
from pymongo import MongoClient
import os

# Define base model class
class Base(DeclarativeBase):
    pass

# Initialize extensions
db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()

# Mongo client (optional)
mongo_client = None
mongo_db = None

def init_mongo(app):
    global mongo_client, mongo_db
    mongo_uri = app.config.get('MONGO_URI') or os.environ.get('MONGO_URI') or 'mongodb://localhost:27017'
    mongo_db_name = app.config.get('MONGO_DB_NAME') or os.environ.get('MONGO_DB_NAME') or 'intelligent_fir'
    try:
        mongo_client = MongoClient(mongo_uri)
        mongo_db = mongo_client[mongo_db_name]
        # ensure indexes
        mongo_db.users.create_index('username', unique=True)
        mongo_db.users.create_index('email', unique=True, sparse=True)
    except Exception as e:
        # Defer errors to runtime usage
        print(f"Warning: Failed to initialize MongoDB: {e}")

@login_manager.user_loader
def load_user(user_id):
    # Import User model here to avoid circular imports
    from models import User
    return User.query.get(int(user_id))
