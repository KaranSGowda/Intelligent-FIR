"""
Debug routes for troubleshooting application issues.
"""

from flask import Blueprint, jsonify, current_app
import os
import logging
import subprocess
import sys
import platform

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
debug_bp = Blueprint('debug', __name__, url_prefix='/api/debug')


