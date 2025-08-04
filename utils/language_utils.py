"""
Language utilities for the Intelligent FIR System.
Provides language codes, names, and translation functionality.
"""

import logging
from flask import session, request

# Configure logging
logger = logging.getLogger(__name__)

# Supported languages with their codes for speech recognition
SUPPORTED_LANGUAGES = {
    'en-US': {
        'name': 'English (US)',
        'native_name': 'English (US)',
        'flag': '🇺🇸',
        'speech_code': 'en-US',
        'direction': 'ltr'
    },
    'en-GB': {
        'name': 'English (UK)',
        'native_name': 'English (UK)',
        'flag': '🇬🇧',
        'speech_code': 'en-GB',
        'direction': 'ltr'
    },
    'en-IN': {
        'name': 'English (India)',
        'native_name': 'English (India)',
        'flag': '🇮🇳',
        'speech_code': 'en-IN',
        'direction': 'ltr'
    },
    'hi-IN': {
        'name': 'Hindi',
        'native_name': 'हिन्दी',
        'flag': '🇮🇳',
        'speech_code': 'hi-IN',
        'direction': 'ltr'
    },
    'bn-IN': {
        'name': 'Bengali',
        'native_name': 'বাংলা',
        'flag': '🇮🇳',
        'speech_code': 'bn-IN',
        'direction': 'ltr'
    },
    'ta-IN': {
        'name': 'Tamil',
        'native_name': 'தமிழ்',
        'flag': '🇮🇳',
        'speech_code': 'ta-IN',
        'direction': 'ltr'
    },
    'te-IN': {
        'name': 'Telugu',
        'native_name': 'తెలుగు',
        'flag': '🇮🇳',
        'speech_code': 'te-IN',
        'direction': 'ltr'
    },
    'mr-IN': {
        'name': 'Marathi',
        'native_name': 'मराठी',
        'flag': '🇮🇳',
        'speech_code': 'mr-IN',
        'direction': 'ltr'
    },
    'gu-IN': {
        'name': 'Gujarati',
        'native_name': 'ગુજરાતી',
        'flag': '🇮🇳',
        'speech_code': 'gu-IN',
        'direction': 'ltr'
    },
    'kn-IN': {
        'name': 'Kannada',
        'native_name': 'ಕನ್ನಡ',
        'flag': '🇮🇳',
        'speech_code': 'kn-IN',
        'direction': 'ltr'
    },
    'ml-IN': {
        'name': 'Malayalam',
        'native_name': 'മലയാളം',
        'flag': '🇮🇳',
        'speech_code': 'ml-IN',
        'direction': 'ltr'
    },
    'pa-IN': {
        'name': 'Punjabi',
        'native_name': 'ਪੰਜਾਬੀ',
        'flag': '🇮🇳',
        'speech_code': 'pa-IN',
        'direction': 'ltr'
    }
}

# Default language code
DEFAULT_LANGUAGE = 'en-IN'

# Basic translations for common UI elements
TRANSLATIONS = {
    'en-US': {
        'file_complaint': 'File a Complaint',
        'record_voice': 'Record Voice',
        'stop_recording': 'Stop Recording',
        'transcribing': 'Transcribing...',
        'analyze_legal': 'Analyze Legal Sections',
        'submit': 'Submit',
        'incident_description': 'Incident Description',
        'incident_date': 'Incident Date & Time',
        'incident_location': 'Incident Location',
        'evidence_upload': 'Upload Evidence',
        'language_select': 'Select Language',
        'ready_to_record': 'Ready to record',
        'recording': 'Recording... Speak now',
        'processing': 'Processing...',
        'transcription_complete': 'Transcription complete',
        'transcription_failed': 'Transcription failed. Please try again or type manually.',
        'analyzing_legal': 'Analyzing applicable IPC sections...',
        'legal_sections': 'Applicable IPC Sections',
        'confidence': 'Confidence',
        'include_in_fir': 'Include in FIR',
        'no_sections_found': 'No applicable IPC sections found. Please review the incident description.'
    },
    'en-GB': {
        # Same as en-US for now
    },
    'en-IN': {
        # Same as en-US for now
    },
    'hi-IN': {
        'file_complaint': 'शिकायत दर्ज करें',
        'record_voice': 'आवाज़ रिकॉर्ड करें',
        'stop_recording': 'रिकॉर्डिंग बंद करें',
        'transcribing': 'प्रतिलेखन हो रहा है...',
        'analyze_legal': 'कानूनी धाराओं का विश्लेषण करें',
        'submit': 'जमा करें',
        'incident_description': 'घटना का विवरण',
        'incident_date': 'घटना की तारीख और समय',
        'incident_location': 'घटना का स्थान',
        'evidence_upload': 'सबूत अपलोड करें',
        'language_select': 'भाषा चुनें',
        'ready_to_record': 'रिकॉर्ड करने के लिए तैयार',
        'recording': 'रिकॉर्डिंग... अब बोलें',
        'processing': 'प्रोसेसिंग...',
        'transcription_complete': 'प्रतिलेखन पूरा हुआ',
        'transcription_failed': 'प्रतिलेखन विफल। कृपया फिर से प्रयास करें या मैन्युअल रूप से टाइप करें।',
        'analyzing_legal': 'लागू IPC धाराओं का विश्लेषण किया जा रहा है...',
        'legal_sections': 'लागू IPC धाराएँ',
        'confidence': 'विश्वास स्तर',
        'include_in_fir': 'FIR में शामिल करें',
        'no_sections_found': 'कोई लागू IPC धारा नहीं मिली। कृपया घटना के विवरण की समीक्षा करें।'
    }
    # Add more translations for other languages as needed
}

def get_user_language():
    """Get the user's preferred language from session or default to browser language."""
    # First check if language is set in session
    if 'language' in session:
        lang_code = session['language']
        if lang_code in SUPPORTED_LANGUAGES:
            return lang_code
    
    # Then check browser's Accept-Language header
    if request.accept_languages:
        for lang_code, _ in request.accept_languages:
            # Check if the language code matches any of our supported languages
            for supported_code in SUPPORTED_LANGUAGES:
                if lang_code.startswith(supported_code.split('-')[0]):
                    return supported_code
    
    # Default to English (India)
    return DEFAULT_LANGUAGE

def set_user_language(lang_code):
    """Set the user's preferred language in session."""
    if lang_code in SUPPORTED_LANGUAGES:
        session['language'] = lang_code
        return True
    return False

def get_translation(key, lang_code=None):
    """Get translation for a key in the specified language."""
    if not lang_code:
        lang_code = get_user_language()
    
    # If language not supported or key not found, fall back to English
    if lang_code not in TRANSLATIONS or key not in TRANSLATIONS[lang_code]:
        return TRANSLATIONS['en-US'].get(key, key)
    
    return TRANSLATIONS[lang_code].get(key, key)

def get_speech_recognition_language(lang_code=None):
    """Get the speech recognition language code."""
    if not lang_code:
        lang_code = get_user_language()
    
    if lang_code in SUPPORTED_LANGUAGES:
        return SUPPORTED_LANGUAGES[lang_code]['speech_code']
    
    return 'en-US'  # Default to US English
