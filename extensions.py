"""
This file contains Flask extensions instances that are used across the application.
Separating these instances helps avoid circular imports.
"""
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager

# Define base model class
class Base(DeclarativeBase):
    pass

# Initialize extensions
db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    # Import User model here to avoid circular imports
    from models import User
    return User.query.get(int(user_id))
