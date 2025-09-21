import os
import logging
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_cors import CORS

# Import extensions
from extensions import db, login_manager

# Try to load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("Loaded environment variables from .env file")
except ImportError:
    print("python-dotenv not installed, skipping .env file loading")

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def create_app():
    # create the app with correct template and static folders
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    templates_path = os.path.join(project_root, 'frontend', 'src', 'templates')
    static_path = os.path.join(project_root, 'frontend', 'static')

    app = Flask(
        __name__,
        template_folder=templates_path,
        static_folder=static_path,
        static_url_path='/static'
    )
    app.secret_key = os.environ.get("SESSION_SECRET", "development_key")
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

    # Enable CORS
    CORS(app)

    # Add custom filters
    @app.template_filter('from_json')
    def from_json(value):
        import json
        try:
            return json.loads(value) if value else []
        except:
            return []

    # configure the database
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///fir_system.db")
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    app.config["UPLOAD_FOLDER"] = os.path.join(app.static_folder, "uploads")
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max upload

    # Base URL for the application (used for QR codes and verification)
    app.config["BASE_URL"] = os.environ.get("BASE_URL", "http://localhost:5000")

    # ensure upload directory exists
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(os.path.join(app.config["UPLOAD_FOLDER"], "images"), exist_ok=True)

    # initialize the app with the extensions
    db.init_app(app)
    login_manager.init_app(app)
    # Mongo configuration
    app.config['MONGO_URI'] = os.environ.get('MONGO_URI', 'mongodb://localhost:27017')
    app.config['MONGO_DB_NAME'] = os.environ.get('MONGO_DB_NAME', 'intelligent_fir')
    from extensions import init_mongo, mongo_db
    init_mongo(app)
    login_manager.login_view = "auth.login"  # type: ignore

    with app.app_context():
        # Import models to ensure they're registered with SQLAlchemy
        import models

        # Add root route
        @app.route('/')
        def index():
            from flask_login import current_user
            from flask import redirect, url_for, render_template

            if current_user.is_authenticated:
                # Redirect authenticated users to their appropriate dashboard
                if current_user.is_admin():
                    return redirect(url_for('admin.dashboard'))
                elif current_user.is_police():
                    return redirect(url_for('admin.cases'))
                else:
                    return redirect(url_for('fir.dashboard'))
            else:
                # Show the homepage for unauthenticated users
                return render_template('index.html')

        # Register blueprints
        from routes.auth import auth_bp
        from routes.fir import fir_bp
        from routes.admin import admin_bp
        from routes.chatbot import chatbot_bp
        from routes.verification import verification_bp
        from routes.evidence import evidence_bp
        from routes.legal_sections import legal_sections_bp
        from routes.debug import debug_bp
        from routes.user_settings import user_settings_bp

        app.register_blueprint(auth_bp)
        app.register_blueprint(fir_bp)
        app.register_blueprint(admin_bp)
        app.register_blueprint(chatbot_bp)
        app.register_blueprint(verification_bp)
        app.register_blueprint(evidence_bp)
        app.register_blueprint(legal_sections_bp)
        app.register_blueprint(debug_bp)
        app.register_blueprint(user_settings_bp)

        # Create all tables
        db.create_all()

        # Seed demo users for testing if they don't exist (SQL)
        try:
            from models import User, Role

            def ensure_demo_user(username: str, role: str, full_name: str):
                existing = User.query.filter_by(username=username).first()
                if not existing:
                    demo = User()
                    demo.username = username
                    demo.email = f"{username}@example.com"
                    demo.full_name = full_name
                    demo.role = role
                    demo.set_password("password")
                    db.session.add(demo)
                    db.session.commit()
                    logger.info(f"Created demo user '{username}' with role '{role}'.")

            ensure_demo_user("user", Role.PUBLIC, "Public User")
            ensure_demo_user("police", Role.POLICE, "Police Officer")
            ensure_demo_user("admin", Role.ADMIN, "Administrator")
        except Exception as e:
            logger.error(f"Error seeding demo users: {str(e)}")

        # Seed demo users into Mongo as well
        try:
            if mongo_db is not None:
                def ensure_mongo_user(username: str, role: str, full_name: str):
                    existing = mongo_db.users.find_one({'username': username})
                    if not existing:
                        from werkzeug.security import generate_password_hash
                        doc = {
                            'username': username,
                            'email': f"{username}@example.com",
                            'full_name': full_name,
                            'role': role,
                            'password_hash': generate_password_hash('password'),
                            'created_at': datetime.utcnow()
                        }
                        mongo_db.users.insert_one(doc)
                        logger.info(f"Seeded Mongo demo user '{username}' ({role})")

                from models import Role as SqlRole  # reuse constants
                from datetime import datetime
                ensure_mongo_user('user', SqlRole.PUBLIC, 'Public User')
                ensure_mongo_user('police', SqlRole.POLICE, 'Police Officer')
                ensure_mongo_user('admin', SqlRole.ADMIN, 'Administrator')
        except Exception as me:
            logger.error(f"Error seeding Mongo demo users: {str(me)}")

        # Initialize legal sections database
        from utils.legal_mapper import initialize_legal_sections
        initialize_legal_sections()

        # Initialize ML model in background thread to avoid blocking app startup
        import threading
        def init_ml_model():
            try:
                from utils.ml_analyzer import train_model
                logger.info("Training ML model in background...")
                train_model()
                logger.info("ML model training completed")
            except Exception as e:
                logger.error(f"Error training ML model: {str(e)}")

        # Start ML model initialization in background
        threading.Thread(target=init_ml_model, daemon=True).start()

    return app

# Note: Do not create or run the app at import time.
# Use the application factory `create_app()` from the entry point (e.g., main.py)
