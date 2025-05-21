"""
Routes for speech recognition and voice-to-text transcription.
"""

from flask import Blueprint, request, jsonify, current_app, session
import os
import uuid
import time
import logging
import importlib
from werkzeug.utils import secure_filename

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
speech_bp = Blueprint('speech', __name__, url_prefix='/api/speech')

# Check if required packages are installed
required_packages = ['speech_recognition', 'pydub']
missing_packages = []

for package in required_packages:
    try:
        importlib.import_module(package)
    except ImportError:
        missing_packages.append(package)
        logger.error(f"Required package '{package}' is not installed")

if missing_packages:
    logger.warning(f"Speech recognition functionality will be limited due to missing packages: {', '.join(missing_packages)}")

# Import speech recognition module only if dependencies are available
if not missing_packages:
    try:
        from utils.speech_recognition import SpeechToText, TranscriptionStatus
        # Initialize speech recognition
        speech_to_text = SpeechToText()
        logger.info("Speech recognition module initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing speech recognition module: {str(e)}", exc_info=True)
        speech_to_text = None
else:
    speech_to_text = None
    logger.error("Speech recognition is disabled due to missing dependencies")

# Store transcription status objects
transcription_tasks = {}

def allowed_audio_file(filename):
    """Check if the file extension is allowed for audio uploads"""
    allowed_extensions = set(['wav', 'mp3', 'ogg', 'flac', 'webm', 'm4a', 'aac', 'mp4', 'amr'])
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

@speech_bp.route('/upload', methods=['POST'])
def upload_audio():
    """
    Upload an audio file for transcription

    Returns:
        JSON with task_id for tracking transcription progress
    """
    # Check if speech recognition is available
    if speech_to_text is None:
        return jsonify({
            'error': 'Speech recognition is not available. Required packages may be missing.',
            'missing_packages': missing_packages
        }), 503  # Service Unavailable

    try:
        # Check if file is in request
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400

        audio_file = request.files['audio']

        # Check if filename is empty
        if audio_file.filename == '':
            return jsonify({'error': 'No audio file selected'}), 400

        # Check if file type is allowed
        if not audio_file.filename or not allowed_audio_file(audio_file.filename):
            return jsonify({'error': 'File type not allowed. Supported formats: WAV, MP3, OGG, FLAC, WebM, M4A, AAC, MP4, AMR'}), 400

        # Get language code from request
        language_code = request.form.get('language')

        # If no language specified, try to get from session
        if not language_code:
            try:
                from utils.language_utils import get_user_language
                language_code = get_user_language()
                logger.info(f"Using language from session: {language_code}")
            except ImportError:
                language_code = "en-IN"  # Default to Indian English
                logger.info(f"Using default language: {language_code}")

        # Generate unique filename
        filename = secure_filename(audio_file.filename or "recording.webm")
        unique_filename = f"{uuid.uuid4()}_{filename}"

        # Create uploads directory if it doesn't exist
        uploads_dir = os.path.join(current_app.root_path, 'uploads', 'audio')
        os.makedirs(uploads_dir, exist_ok=True)

        # Save the file
        file_path = os.path.join(uploads_dir, unique_filename)
        audio_file.save(file_path)

        # Generate task ID
        task_id = str(uuid.uuid4())

        # Start transcription in background
        def callback(status_dict):
            # Update the task status
            transcription_tasks[task_id] = status_dict

            # Clean up completed or failed tasks after 1 hour
            if status_dict['status'] in ['completed', 'failed']:
                # Schedule cleanup
                def cleanup():
                    if task_id in transcription_tasks:
                        del transcription_tasks[task_id]
                    # Delete the audio file
                    try:
                        if os.path.exists(file_path):
                            os.remove(file_path)
                    except Exception as e:
                        logger.error(f"Error deleting audio file: {str(e)}")

                # Use a simple thread for cleanup after 1 hour
                import threading
                cleanup_thread = threading.Timer(3600, cleanup)
                cleanup_thread.daemon = True
                cleanup_thread.start()

        # Start transcription asynchronously with specified language
        logger.info(f"Starting async transcription with language: {language_code}")
        status = speech_to_text.transcribe_audio_async(file_path, callback, language_code)

        # Store initial status
        transcription_tasks[task_id] = status.to_dict()

        # Return task ID for status polling
        return jsonify({
            'task_id': task_id,
            'message': f'Audio file uploaded successfully, transcription in progress with language: {language_code}',
            'language': language_code,
            'status': status.to_dict()
        })

    except Exception as e:
        logger.error(f"Error processing audio upload: {str(e)}", exc_info=True)
        return jsonify({'error': f'Error processing audio: {str(e)}'}), 500

@speech_bp.route('/status/<task_id>', methods=['GET'])
def get_transcription_status(task_id):
    """
    Get the status of a transcription task

    Args:
        task_id: The ID of the transcription task

    Returns:
        JSON with the current status of the transcription
    """
    # Check if speech recognition is available
    if speech_to_text is None:
        return jsonify({
            'error': 'Speech recognition is not available. Required packages may be missing.',
            'missing_packages': missing_packages
        }), 503  # Service Unavailable

    if task_id not in transcription_tasks:
        return jsonify({'error': 'Task not found'}), 404

    return jsonify(transcription_tasks[task_id])

@speech_bp.route('/transcribe', methods=['POST'])
def transcribe_audio():
    """
    Synchronous transcription endpoint

    This endpoint blocks until transcription is complete

    Returns:
        JSON with transcription result
    """
    # Check if speech recognition is available
    if speech_to_text is None:
        return jsonify({
            'error': 'Speech recognition is not available. Required packages may be missing.',
            'missing_packages': missing_packages
        }), 503  # Service Unavailable

    try:
        # Check if file is in request
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400

        audio_file = request.files['audio']

        # Check if filename is empty
        if audio_file.filename == '':
            return jsonify({'error': 'No audio file selected'}), 400

        # Check if file type is allowed
        if not audio_file.filename or not allowed_audio_file(audio_file.filename):
            return jsonify({'error': 'File type not allowed. Supported formats: WAV, MP3, OGG, FLAC, WebM, M4A, AAC, MP4, AMR'}), 400

        # Get language code from request
        language_code = request.form.get('language')

        # If no language specified, try to get from session
        if not language_code:
            try:
                from utils.language_utils import get_user_language
                language_code = get_user_language()
                logger.info(f"Using language from session: {language_code}")
            except ImportError:
                language_code = "en-IN"  # Default to Indian English
                logger.info(f"Using default language: {language_code}")

        # Generate unique filename
        filename = secure_filename(audio_file.filename or "recording.webm")
        unique_filename = f"{uuid.uuid4()}_{filename}"

        # Create uploads directory if it doesn't exist
        uploads_dir = os.path.join(current_app.root_path, 'uploads', 'audio')
        os.makedirs(uploads_dir, exist_ok=True)

        # Save the file
        file_path = os.path.join(uploads_dir, unique_filename)
        audio_file.save(file_path)

        # Create status object for tracking
        from utils.speech_recognition import TranscriptionStatus
        status = TranscriptionStatus()

        # Perform transcription (blocking) with specified language
        logger.info(f"Starting transcription with language: {language_code}")
        result = speech_to_text.transcribe_audio(file_path, status, language_code)

        # Delete the file after transcription
        try:
            os.remove(file_path)
        except Exception as e:
            logger.warning(f"Failed to delete temporary file: {str(e)}")

        # Return the result
        return jsonify({
            'transcription': result,
            'language': language_code,
            'status': status.to_dict()
        })

    except Exception as e:
        logger.error(f"Error transcribing audio: {str(e)}", exc_info=True)
        return jsonify({'error': f'Error transcribing audio: {str(e)}'}), 500

@speech_bp.route('/languages', methods=['GET'])
def get_supported_languages():
    """
    Get list of supported languages for speech recognition

    Returns:
        JSON with list of supported languages
    """
    try:
        # Import language utilities
        from utils.language_utils import SUPPORTED_LANGUAGES, get_user_language

        # Convert to list format for API
        languages = []
        for code, lang_info in SUPPORTED_LANGUAGES.items():
            languages.append({
                "code": code,
                "name": lang_info["name"],
                "native_name": lang_info["native_name"],
                "flag": lang_info["flag"],
                "direction": lang_info["direction"]
            })

        # Get current user language
        current_language = get_user_language()

        # Add speech recognition status
        speech_recognition_status = {
            "available": speech_to_text is not None,
            "missing_packages": missing_packages if missing_packages else []
        }

        return jsonify({
            "languages": languages,
            "current": current_language,
            "speech_recognition": speech_recognition_status
        })
    except ImportError:
        # Fallback if language_utils is not available
        languages = [
            {"code": "en-US", "name": "English (US)", "native_name": "English (US)", "flag": "🇺🇸", "direction": "ltr"},
            {"code": "en-GB", "name": "English (UK)", "native_name": "English (UK)", "flag": "🇬🇧", "direction": "ltr"},
            {"code": "en-IN", "name": "English (India)", "native_name": "English (India)", "flag": "🇮🇳", "direction": "ltr"},
            {"code": "hi-IN", "name": "Hindi", "native_name": "हिन्दी", "flag": "🇮🇳", "direction": "ltr"},
            {"code": "bn-IN", "name": "Bengali", "native_name": "বাংলা", "flag": "🇮🇳", "direction": "ltr"},
            {"code": "ta-IN", "name": "Tamil", "native_name": "தமிழ்", "flag": "🇮🇳", "direction": "ltr"},
            {"code": "te-IN", "name": "Telugu", "native_name": "తెలుగు", "flag": "🇮🇳", "direction": "ltr"},
            {"code": "mr-IN", "name": "Marathi", "native_name": "मराठी", "flag": "🇮🇳", "direction": "ltr"},
            {"code": "gu-IN", "name": "Gujarati", "native_name": "ગુજરાતી", "flag": "🇮🇳", "direction": "ltr"},
            {"code": "kn-IN", "name": "Kannada", "native_name": "ಕನ್ನಡ", "flag": "🇮🇳", "direction": "ltr"},
            {"code": "ml-IN", "name": "Malayalam", "native_name": "മലയാളം", "flag": "🇮🇳", "direction": "ltr"},
            {"code": "pa-IN", "name": "Punjabi", "native_name": "ਪੰਜਾਬੀ", "flag": "🇮🇳", "direction": "ltr"},
        ]

        # Add speech recognition status
        speech_recognition_status = {
            "available": speech_to_text is not None,
            "missing_packages": missing_packages if missing_packages else []
        }

        return jsonify({
            "languages": languages,
            "current": "en-IN",
            "speech_recognition": speech_recognition_status
        })

@speech_bp.route('/test', methods=['GET'])
def test_speech_recognition():
    """
    Test endpoint to check if speech recognition is working

    Returns:
        JSON with status of speech recognition
    """
    # Check for required packages
    package_status = {}
    for package in ['speech_recognition', 'pydub']:
        try:
            module = importlib.import_module(package)
            if package == 'speech_recognition':
                package_status[package] = {
                    'installed': True,
                    'version': getattr(module, '__version__', 'unknown')
                }
            else:
                package_status[package] = {
                    'installed': True,
                    'version': getattr(module, 'version', 'unknown')
                }
        except ImportError:
            package_status[package] = {
                'installed': False,
                'error': f"Package '{package}' is not installed"
            }

    # Check if uploads directory exists
    uploads_dir = os.path.join(current_app.root_path, 'uploads', 'audio')
    try:
        os.makedirs(uploads_dir, exist_ok=True)
        directory_status = {
            'exists': os.path.exists(uploads_dir),
            'writable': os.access(uploads_dir, os.W_OK),
            'path': uploads_dir
        }
    except Exception as e:
        directory_status = {
            'exists': False,
            'writable': False,
            'error': str(e),
            'path': uploads_dir
        }

    # Check speech recognition module
    module_status = {
        'initialized': speech_to_text is not None,
        'missing_packages': missing_packages
    }

    # Return comprehensive status
    return jsonify({
        'status': 'success' if speech_to_text is not None else 'error',
        'message': 'Speech recognition is working correctly' if speech_to_text is not None else 'Speech recognition is not available',
        'packages': package_status,
        'directory': directory_status,
        'module': module_status,
        'installation_instructions': {
            'speech_recognition': 'pip install SpeechRecognition',
            'pydub': 'pip install pydub',
            'ffmpeg': 'Install ffmpeg from https://ffmpeg.org/download.html or use your system package manager'
        }
    })
