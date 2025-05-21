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

@debug_bp.route('/speech-recognition', methods=['GET'])
def check_speech_recognition():
    """
    Check if speech recognition dependencies are properly installed
    """
    try:
        results = {
            'python_version': sys.version,
            'platform': platform.platform(),
            'dependencies': {},
            'ffmpeg': False,
            'uploads_dir': False,
            'temp_dir_writable': False
        }
        
        # Check SpeechRecognition
        try:
            import speech_recognition
            results['dependencies']['speech_recognition'] = {
                'installed': True,
                'version': speech_recognition.__version__
            }
        except ImportError as e:
            results['dependencies']['speech_recognition'] = {
                'installed': False,
                'error': str(e)
            }
        
        # Check pydub
        try:
            import pydub
            results['dependencies']['pydub'] = {
                'installed': True,
                'version': pydub.__version__
            }
        except ImportError as e:
            results['dependencies']['pydub'] = {
                'installed': False,
                'error': str(e)
            }
        
        # Check ffmpeg
        try:
            ffmpeg_output = subprocess.check_output(['ffmpeg', '-version'], stderr=subprocess.STDOUT)
            results['ffmpeg'] = {
                'installed': True,
                'version': ffmpeg_output.decode('utf-8').split('\\n')[0]
            }
        except (subprocess.SubprocessError, FileNotFoundError) as e:
            results['ffmpeg'] = {
                'installed': False,
                'error': str(e)
            }
        
        # Check uploads directory
        uploads_dir = os.path.join(current_app.root_path, 'uploads', 'audio')
        results['uploads_dir'] = {
            'path': uploads_dir,
            'exists': os.path.exists(uploads_dir),
            'writable': os.access(uploads_dir, os.W_OK) if os.path.exists(uploads_dir) else False
        }
        
        # Create directory if it doesn't exist
        if not os.path.exists(uploads_dir):
            try:
                os.makedirs(uploads_dir, exist_ok=True)
                results['uploads_dir']['created'] = True
                results['uploads_dir']['exists'] = True
                results['uploads_dir']['writable'] = os.access(uploads_dir, os.W_OK)
            except Exception as e:
                results['uploads_dir']['creation_error'] = str(e)
        
        # Check temp directory
        import tempfile
        temp_dir = tempfile.gettempdir()
        results['temp_dir_writable'] = {
            'path': temp_dir,
            'writable': os.access(temp_dir, os.W_OK)
        }
        
        return jsonify(results)
    except Exception as e:
        logger.error(f"Error in debug route: {str(e)}", exc_info=True)
        return jsonify({
            'error': str(e),
            'traceback': str(e.__traceback__)
        }), 500
