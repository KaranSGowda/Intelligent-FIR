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
    # create the app
    app = Flask(__name__)
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
    app.config["UPLOAD_FOLDER"] = "static/uploads"
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max upload

    # Base URL for the application (used for QR codes and verification)
    app.config["BASE_URL"] = os.environ.get("BASE_URL", "http://localhost:5000")

    # ensure upload directory exists
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(os.path.join(app.config["UPLOAD_FOLDER"], "audio"), exist_ok=True)
    os.makedirs(os.path.join(app.config["UPLOAD_FOLDER"], "images"), exist_ok=True)

    # initialize the app with the extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"  # type: ignore

    with app.app_context():
        # Import models to ensure they're registered with SQLAlchemy
        import models

        # Register blueprints
        from routes.auth import auth_bp
        from routes.fir import fir_bp
        from routes.admin import admin_bp
        from routes.chatbot import chatbot_bp
        from routes.speech_recognition import speech_bp
        from routes.verification import verification_bp
        from routes.evidence import evidence_bp
        from routes.legal_sections import legal_sections_bp
        from routes.debug import debug_bp
        from routes.user_settings import user_settings_bp

        app.register_blueprint(auth_bp)
        app.register_blueprint(fir_bp)
        app.register_blueprint(admin_bp)
        app.register_blueprint(chatbot_bp)
        app.register_blueprint(speech_bp)
        app.register_blueprint(verification_bp)
        app.register_blueprint(evidence_bp)
        app.register_blueprint(legal_sections_bp)
        app.register_blueprint(debug_bp)
        app.register_blueprint(user_settings_bp)

        # Create all tables
        db.create_all()

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

# Create the application instance
app = create_app()




