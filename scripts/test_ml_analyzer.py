"""
Script to directly test the ML analyzer with specific case descriptions.
"""

import logging
import sys
import os

# Set environment variables for Flask
os.environ["FLASK_APP"] = "app.py"
os.environ["FLASK_ENV"] = "development"
os.environ["DATABASE_URL"] = "sqlite:///fir_system.db"

# Configure logging to output to console
logging.basicConfig(level=logging.INFO,
                    format='%(levelname)s:%(name)s:%(message)s',
                    handlers=[logging.StreamHandler(sys.stdout)])

def test_analyzer(description):
    """Test the ML analyzer with a specific case description."""
    print(f"Testing ML analyzer with: '{description}'")

    # Import Flask app and create application context
    try:
        from app import create_app
        app = create_app()

        # Use app context for database operations
        with app.app_context():
            # Import the ML analyzer
            from utils.ml_analyzer import analyze_complaint

            # Analyze the complaint
            result = analyze_complaint(description)

            # Print the results
            print("\nAnalysis Results:")
            print("-" * 80)

            if not result or not result.get('sections'):
                print("No applicable IPC sections found.")
                return

            # Get sections and sort by confidence
            sections = result.get('sections', [])
            sections = sorted(sections, key=lambda s: s.get('confidence', 0), reverse=True)

            # Print top 5 sections
            for i, section in enumerate(sections[:5], 1):
                confidence = section.get('confidence', 0)
                print(f"{i}. Section {section['section_code']}: {section['section_name']} (Confidence: {confidence:.2%})")
                print(f"   Description: {section['section_description']}")
                if section.get('keywords_matched'):
                    print(f"   Keywords matched: {', '.join(section.get('keywords_matched', []))}")
                print()

    except Exception as e:
        print(f"Error testing ML analyzer: {str(e)}")

if __name__ == "__main__":
    # Test with various case descriptions
    test_cases = [
        "Someone broke into my house and stole my laptop and jewelry",
        "I was assaulted by my neighbor who hit me with his fists",
        "A person murdered someone by stabbing them multiple times",
        "My boss has been sexually harassing me at work",
        "I was cheated by an online seller who took my money but never delivered the product",
        "A public servant negligently allowed a prisoner to escape",
        "Someone forged my signature on a document",
        "The beauty of the sunset was absolutely killing me"  # Figurative language test
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n=== Test Case {i}/{len(test_cases)} ===")
        test_analyzer(test_case)
        print("=" * 80)
