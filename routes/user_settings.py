"""
Routes for user settings and preferences.
"""

from flask import Blueprint, request, jsonify, session
import logging
from utils.language_utils import set_user_language, get_user_language, SUPPORTED_LANGUAGES

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
user_settings_bp = Blueprint('user_settings', __name__, url_prefix='/api/user')

@user_settings_bp.route('/set-language', methods=['POST'])
def set_language():
    """
    Set the user's preferred language
    
    Expects JSON with language code:
    {
        "language": "en-US"
    }
    
    Returns:
        JSON with success status
    """
    try:
        data = request.json
        if not data or 'language' not in data:
            return jsonify({'success': False, 'error': 'No language specified'}), 400
            
        language_code = data['language']
        
        # Validate language code
        if language_code not in SUPPORTED_LANGUAGES:
            return jsonify({
                'success': False, 
                'error': f'Unsupported language: {language_code}',
                'supported_languages': list(SUPPORTED_LANGUAGES.keys())
            }), 400
            
        # Set language in session
        success = set_user_language(language_code)
        
        if success:
            logger.info(f"Language set to {language_code} for user")
            return jsonify({'success': True, 'language': language_code})
        else:
            return jsonify({'success': False, 'error': 'Failed to set language'}), 500
            
    except Exception as e:
        logger.error(f"Error setting language: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500
        
@user_settings_bp.route('/get-language', methods=['GET'])
def get_language():
    """
    Get the user's preferred language
    
    Returns:
        JSON with language code and info
    """
    try:
        language_code = get_user_language()
        
        if language_code in SUPPORTED_LANGUAGES:
            language_info = SUPPORTED_LANGUAGES[language_code]
            return jsonify({
                'success': True,
                'language': language_code,
                'name': language_info['name'],
                'native_name': language_info['native_name'],
                'flag': language_info['flag'],
                'direction': language_info['direction']
            })
        else:
            return jsonify({'success': False, 'error': f'Unsupported language: {language_code}'}), 400
            
    except Exception as e:
        logger.error(f"Error getting language: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500
