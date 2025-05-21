import os
import logging
from flask import Flask, render_template, jsonify, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager, login_required, current_user

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

# Initialize app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "development_key")

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///fir_system.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize extensions
db = SQLAlchemy(model_class=Base)
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Simplified routes
@app.route('/')
def index():
    logger.info("Index route accessed")
    return render_template('index.html')

@app.route('/health')
def health():
    logger.info("Health check requested")
    return jsonify({"status": "healthy"})

# Load user function
@login_manager.user_loader
def load_user(user_id):
    from models import User
    return db.session.get(User, int(user_id))

# Create database tables
with app.app_context():
    # Import models to register them with SQLAlchemy
    import models
    
    # Only create tables in development
    if app.config["SQLALCHEMY_DATABASE_URI"].startswith("sqlite"):
        db.create_all()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"Starting minimal application on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)