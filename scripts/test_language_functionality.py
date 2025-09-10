#!/usr/bin/env python3
"""
Test script for language functionality in the Intelligent-FIR system.
This script tests language selection, translations, and multilingual features.
"""

import os
import sys
import logging
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app import create_app
from utils.language_utils import (
    SUPPORTED_LANGUAGES, 
    get_user_language, 
    set_user_language, 
    get_translation,
    get_speech_recognition_language
)
from utils.multilingual_training_data import (
    get_multilingual_training_data,
    get_language_keywords,
    get_supported_languages
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_language_configuration():
    """
    Test the language configuration and supported languages.
    """
    logger.info("Testing Language Configuration")
    logger.info("=" * 50)
    
    # Test supported languages
    logger.info(f"Number of supported languages: {len(SUPPORTED_LANGUAGES)}")
    
    for lang_code, lang_info in SUPPORTED_LANGUAGES.items():
        logger.info(f"{lang_code}: {lang_info['name']} ({lang_info['native_name']})")
        logger.info(f"  Flag: {lang_info['flag']}")
        logger.info(f"  Speech Code: {lang_info['speech_code']}")
        logger.info(f"  Direction: {lang_info['direction']}")
        logger.info()
    
    logger.info("Language configuration test completed!")
    logger.info()

def test_language_functions():
    """
    Test language utility functions.
    """
    logger.info("Testing Language Utility Functions")
    logger.info("=" * 50)
    
    # Test with Flask app context
    app = create_app()
    
    with app.app_context():
        # Test default language
        default_lang = get_user_language()
        logger.info(f"Default language: {default_lang}")
        
        # Test setting different languages
        test_languages = ['hi-IN', 'ta-IN', 'bn-IN', 'te-IN', 'en-IN']
        
        for lang in test_languages:
            success = set_user_language(lang)
            current_lang = get_user_language()
            speech_lang = get_speech_recognition_language()
            
            logger.info(f"Set language to {lang}: {'Success' if success else 'Failed'}")
            logger.info(f"Current language: {current_lang}")
            logger.info(f"Speech recognition language: {speech_lang}")
            logger.info()
    
    logger.info("Language utility functions test completed!")
    logger.info()

def test_translations():
    """
    Test UI translations for different languages.
    """
    logger.info("Testing UI Translations")
    logger.info("=" * 50)
    
    # Test translation keys
    translation_keys = [
        'file_complaint',
        'record_voice', 
        'stop_recording',
        'transcribing',
        'analyze_legal',
        'submit',
        'incident_description',
        'incident_date',
        'incident_location',
        'evidence_upload',
        'language_select'
    ]
    
    # Test languages that have translations
    test_languages = ['en-US', 'hi-IN']
    
    for lang in test_languages:
        logger.info(f"Translations for {lang}:")
        for key in translation_keys:
            translation = get_translation(key, lang)
            logger.info(f"  {key}: {translation}")
        logger.info()
    
    logger.info("UI translations test completed!")
    logger.info()

def test_multilingual_training_data():
    """
    Test multilingual training data functionality.
    """
    logger.info("Testing Multilingual Training Data")
    logger.info("=" * 50)
    
    # Test supported languages
    supported_langs = get_supported_languages()
    logger.info(f"Languages with training data: {supported_langs}")
    
    # Test training data for each language
    for lang in supported_langs:
        training_data = get_multilingual_training_data(lang)
        logger.info(f"{lang}: {len(training_data)} training examples")
        
        # Show a few examples
        for i, (text, sections) in enumerate(training_data[:3]):
            logger.info(f"  Example {i+1}: {text[:50]}... -> {sections}")
        logger.info()
    
    # Test keywords
    for lang in supported_langs:
        keywords = get_language_keywords(lang)
        logger.info(f"{lang} keywords for IPC sections:")
        for section, section_keywords in keywords.items():
            logger.info(f"  {section}: {section_keywords[:3]}...")  # Show first 3 keywords
        logger.info()
    
    logger.info("Multilingual training data test completed!")
    logger.info()

def test_speech_recognition_languages():
    """
    Test speech recognition language codes.
    """
    logger.info("Testing Speech Recognition Languages")
    logger.info("=" * 50)
    
    test_languages = ['en-US', 'en-IN', 'hi-IN', 'ta-IN', 'bn-IN', 'te-IN']
    
    for lang in test_languages:
        speech_code = get_speech_recognition_language(lang)
        logger.info(f"{lang} -> Speech Code: {speech_code}")
    
    logger.info("Speech recognition languages test completed!")
    logger.info()

def test_language_selector_api():
    """
    Test the language selector API endpoint.
    """
    logger.info("Testing Language Selector API")
    logger.info("=" * 50)
    
    app = create_app()
    
    with app.test_client() as client:
        # Test the languages endpoint
        response = client.get('/api/speech/languages')
        
        if response.status_code == 200:
            data = response.get_json()
            logger.info("API Response:")
            logger.info(f"  Current language: {data.get('current')}")
            logger.info(f"  Number of languages: {len(data.get('languages', []))}")
            
            # Show first few languages
            for lang in data.get('languages', [])[:5]:
                logger.info(f"  {lang['code']}: {lang['name']} ({lang['native_name']})")
            
            # Test speech recognition status
            speech_status = data.get('speech_recognition', {})
            logger.info(f"  Speech recognition available: {speech_status.get('available')}")
            
        else:
            logger.error(f"API request failed with status code: {response.status_code}")
    
    logger.info("Language selector API test completed!")
    logger.info()

def interactive_language_test():
    """
    Interactive test for language functionality.
    """
    logger.info("Interactive Language Test")
    logger.info("=" * 50)
    
    print("\nAvailable languages:")
    for i, (lang_code, lang_info) in enumerate(SUPPORTED_LANGUAGES.items(), 1):
        print(f"{i}. {lang_info['flag']} {lang_info['name']} ({lang_info['native_name']})")
    
    try:
        choice = input("\nSelect a language number to test (or press Enter to skip): ").strip()
        if choice:
            choice_idx = int(choice) - 1
            lang_codes = list(SUPPORTED_LANGUAGES.keys())
            if 0 <= choice_idx < len(lang_codes):
                selected_lang = lang_codes[choice_idx]
                lang_info = SUPPORTED_LANGUAGES[selected_lang]
                
                print(f"\nTesting language: {lang_info['name']}")
                print(f"Native name: {lang_info['native_name']}")
                print(f"Speech code: {lang_info['speech_code']}")
                
                # Show some translations
                test_keys = ['file_complaint', 'record_voice', 'submit']
                print("\nSample translations:")
                for key in test_keys:
                    translation = get_translation(key, selected_lang)
                    print(f"  {key}: {translation}")
                
                # Show some training examples
                training_data = get_multilingual_training_data(selected_lang)
                if training_data:
                    print(f"\nSample training examples ({len(training_data)} total):")
                    for i, (text, sections) in enumerate(training_data[:3]):
                        print(f"  {i+1}. {text[:60]}... -> {sections}")
                
            else:
                print("Invalid choice!")
    except (ValueError, KeyboardInterrupt):
        print("Test skipped or interrupted.")
    
    logger.info("Interactive language test completed!")
    logger.info()

def main():
    """
    Main function to run all language tests.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Test language functionality')
    parser.add_argument('--config', action='store_true', help='Test language configuration')
    parser.add_argument('--functions', action='store_true', help='Test language utility functions')
    parser.add_argument('--translations', action='store_true', help='Test UI translations')
    parser.add_argument('--training', action='store_true', help='Test multilingual training data')
    parser.add_argument('--speech', action='store_true', help='Test speech recognition languages')
    parser.add_argument('--api', action='store_true', help='Test language selector API')
    parser.add_argument('--interactive', action='store_true', help='Run interactive language test')
    parser.add_argument('--all', action='store_true', help='Run all tests')
    
    args = parser.parse_args()
    
    if args.all or not any([args.config, args.functions, args.translations, 
                           args.training, args.speech, args.api, args.interactive]):
        # Run all tests by default
        test_language_configuration()
        test_language_functions()
        test_translations()
        test_multilingual_training_data()
        test_speech_recognition_languages()
        test_language_selector_api()
        interactive_language_test()
    else:
        # Run specific tests
        if args.config:
            test_language_configuration()
        if args.functions:
            test_language_functions()
        if args.translations:
            test_translations()
        if args.training:
            test_multilingual_training_data()
        if args.speech:
            test_speech_recognition_languages()
        if args.api:
            test_language_selector_api()
        if args.interactive:
            interactive_language_test()
    
    logger.info("All language functionality tests completed!")

if __name__ == '__main__':
    main() 