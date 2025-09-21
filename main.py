#!/usr/bin/env python3
"""
Main entry point for the Intelligent FIR System
This file serves as the entry point to run the Flask application
"""

import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Import and run the Flask app
from backend.app import create_app

if __name__ == '__main__':
    app = create_app()
    # Disable the reloader to avoid Windows socket OSError when threads/background tasks are used
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
