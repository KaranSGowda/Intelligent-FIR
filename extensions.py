"""Extensions Module

This file contains Flask extensions instances that are used across the application.
Separating these instances helps avoid circular imports.

The extensions are initialized here and imported where needed, rather than
creating them in the main application file. This pattern helps prevent
circular dependencies between modules.
"""
The Flask extensions instances used across the application are defined here.
Separating these instances helps avoid circular imports.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    # Import User model here to avoid circular imports
    from models import User
    return User.query.get(int(user_id))
