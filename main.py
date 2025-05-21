import os

# Try to load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("Loaded environment variables from .env file")
except ImportError:
    print("python-dotenv not installed, skipping .env file loading")

# Set default environment variables if not already set
os.environ.setdefault("FLASK_APP", "app.py")
os.environ.setdefault("FLASK_ENV", "development")
os.environ.setdefault("FLASK_DEBUG", "1")
os.environ.setdefault("SECRET_KEY", os.environ.get("SECRET_KEY", "your-secret-key-here"))
# Set SQLite as the default database
os.environ.setdefault("DATABASE_URL", "sqlite:///fir_system.db")

from app import create_app

if __name__ == "__main__":
    print("Starting Flask application on port 5000...")
    app = create_app()

    # Get port from environment variable or use 5000 as default
    port = int(os.environ.get("PORT", 5000))

    # Run the app
    app.run(host="0.0.0.0", port=port, debug=True)
