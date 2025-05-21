import os
import logging
from flask import Flask, jsonify

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create a simple Flask app
app = Flask(__name__)

@app.route('/')
def index():
    logger.info("Index route accessed")
    return jsonify({
        "status": "success",
        "message": "Debug application is running",
        "env_vars": {
            "DATABASE_URL": os.environ.get("DATABASE_URL", "Not set"),
            "OPENAI_API_KEY": "Present" if os.environ.get("OPENAI_API_KEY") else "Not set",
            "SESSION_SECRET": "Present" if os.environ.get("SESSION_SECRET") else "Not set"
        }
    })

@app.route('/health')
def health():
    logger.info("Health check requested")
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"Starting debug application on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)