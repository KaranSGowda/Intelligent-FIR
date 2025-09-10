#!/usr/bin/env python3
"""
Script to train the ML model with multilingual training data.
This script combines training data from multiple languages to improve
the model's ability to classify complaints in different languages.
"""

import os
import sys
import logging
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app import create_app
from utils.ml_analyzer import train_model
from utils.training_data import TRAINING_DATA
from utils.multilingual_training_data import get_multilingual_training_data, get_supported_languages

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def train_multilingual_model():
    """
    Train the ML model with multilingual training data.
    """
    try:
        # Create Flask app context
        app = create_app()
        
        with app.app_context():
            logger.info("Starting multilingual model training...")
            
            # Get all multilingual training data
            multilingual_data = get_multilingual_training_data()
            
            # Get English training data
            english_data = TRAINING_DATA
            
            # Combine all training data
            combined_training_data = english_data + multilingual_data
            
            # Log statistics
            logger.info(f"English training examples: {len(english_data)}")
            logger.info(f"Multilingual training examples: {len(multilingual_data)}")
            logger.info(f"Total training examples: {len(combined_training_data)}")
            
            # Count examples by language
            supported_languages = get_supported_languages()
            for lang in supported_languages:
                lang_data = get_multilingual_training_data(lang)
                logger.info(f"{lang} training examples: {len(lang_data)}")
            
            # Count unique IPC sections
            all_sections = set()
            for _, sections in combined_training_data:
                all_sections.update(sections)
            
            logger.info(f"Unique IPC sections in training data: {len(all_sections)}")
            logger.info(f"IPC sections: {sorted(all_sections)}")
            
            # Train the model with combined data
            logger.info("Training model with combined multilingual data...")
            train_model(combined_training_data)
            
            logger.info("Multilingual model training completed successfully!")
            
            # Test the model with some examples
            test_multilingual_classification()
            
    except Exception as e:
        logger.error(f"Error during multilingual model training: {str(e)}")
        raise

def test_multilingual_classification():
    """
    Test the trained model with multilingual examples.
    """
    try:
        from utils.ml_analyzer import analyze_complaint
        
        logger.info("Testing multilingual classification...")
        
        # Test examples in different languages
        test_cases = [
            # Hindi examples
            ("आरोपी ने पीड़ित को चाकू से मार डाला।", "hi-IN"),
            ("आरोपी ने पीड़ित को धोखा दिया।", "hi-IN"),
            ("आरोपी ने पीड़ित को मारा-पीटा।", "hi-IN"),
            
            # Tamil examples
            ("குற்றவாளி பாதிக்கப்பட்டவரை கத்தியால் கொன்றார்.", "ta-IN"),
            ("குற்றவாளி பாதிக்கப்பட்டவரை ஏமாற்றினார்.", "ta-IN"),
            ("குற்றவாளி பாதிக்கப்பட்டவரை அடித்து உதைத்தார்.", "ta-IN"),
            
            # Bengali examples
            ("অভিযুক্ত ব্যক্তি ছুরি দিয়ে ভিকটিমকে হত্যা করেছে।", "bn-IN"),
            ("অভিযুক্ত ব্যক্তি ভিকটিমকে প্রতারণা করেছে।", "bn-IN"),
            ("অভিযুক্ত ব্যক্তি ভিকটিমকে মারধর করেছে।", "bn-IN"),
            
            # Telugu examples
            ("అభియుక్తుడు కత్తితో బాధితుడిని చంపాడు.", "te-IN"),
            ("అభియుక్తుడు బాధితుడిని మోసం చేశాడు.", "te-IN"),
            ("అభియుక్తుడు బాధితుడిని కొట్టాడు.", "te-IN"),
            
            # English examples
            ("The accused murdered the victim with a knife.", "en-IN"),
            ("The accused cheated the victim.", "en-IN"),
            ("The accused assaulted the victim.", "en-IN"),
        ]
        
        for text, language in test_cases:
            try:
                result = analyze_complaint(text)
                logger.info(f"Language: {language}")
                logger.info(f"Text: {text}")
                logger.info(f"Result: {result}")
                logger.info("-" * 50)
            except Exception as e:
                logger.error(f"Error testing {language} example: {str(e)}")
                
    except Exception as e:
        logger.error(f"Error during multilingual classification testing: {str(e)}")

def analyze_training_data_coverage():
    """
    Analyze the coverage of training data across languages and IPC sections.
    """
    try:
        logger.info("Analyzing training data coverage...")
        
        # Get training data by language
        supported_languages = get_supported_languages()
        language_stats = {}
        
        for lang in supported_languages:
            lang_data = get_multilingual_training_data(lang)
            sections = set()
            for _, section_list in lang_data:
                sections.update(section_list)
            
            language_stats[lang] = {
                'examples': len(lang_data),
                'sections': len(sections),
                'section_list': sorted(sections)
            }
        
        # Print statistics
        logger.info("Training Data Coverage Analysis:")
        logger.info("=" * 60)
        
        for lang, stats in language_stats.items():
            logger.info(f"{lang}:")
            logger.info(f"  Examples: {stats['examples']}")
            logger.info(f"  IPC Sections: {stats['sections']}")
            logger.info(f"  Sections: {stats['section_list']}")
            logger.info()
        
        # Overall statistics
        all_data = get_multilingual_training_data()
        all_sections = set()
        for _, section_list in all_data:
            all_sections.update(section_list)
        
        logger.info(f"Overall Statistics:")
        logger.info(f"  Total Examples: {len(all_data)}")
        logger.info(f"  Total IPC Sections: {len(all_sections)}")
        logger.info(f"  All Sections: {sorted(all_sections)}")
        
    except Exception as e:
        logger.error(f"Error during coverage analysis: {str(e)}")

def main():
    """
    Main function to run the multilingual training process.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Train ML model with multilingual data')
    parser.add_argument('--analyze-only', action='store_true', 
                       help='Only analyze training data coverage without training')
    parser.add_argument('--test-only', action='store_true',
                       help='Only test the existing model without training')
    
    args = parser.parse_args()
    
    if args.analyze_only:
        analyze_training_data_coverage()
    elif args.test_only:
        test_multilingual_classification()
    else:
        # Full training process
        analyze_training_data_coverage()
        train_multilingual_model()

if __name__ == '__main__':
    main() 