"""
Test the preprocessing function in the ML analyzer.
"""

import os
import sys

# Set environment variables for Flask
os.environ["FLASK_APP"] = "app.py"
os.environ["FLASK_ENV"] = "development"
os.environ["DATABASE_URL"] = "sqlite:///fir_system.db"

# Import Flask app and create application context
from app import create_app
app = create_app()

# Use app context for database operations
with app.app_context():
    # Import the ML analyzer
    from utils.ml_analyzer import preprocess_text, analyze_complaint

    # Test preprocessing with various misspellings
    test_cases = [
        "i mudered a person",
        "someone was murderd yesterday",
        "he stabed me with a knife",
        "i was robed at gunpoint",
        "the theif stole my wallet",
        "i was asaulted by my neighbor",
        "someone is harrasing me online",
        "i was cheeted by a seller",
        "my child was kidnaped",
        "i was defamed on social media"
    ]

    print("Testing preprocessing function:")
    print("-" * 80)
    for i, test_case in enumerate(test_cases, 1):
        processed = preprocess_text(test_case)
        print(f"{i}. Original: '{test_case}'")
        print(f"   Processed: '{processed}'")
        print()

    print("\nTesting complaint analysis with misspellings:")
    print("-" * 80)
    for i, test_case in enumerate(test_cases, 1):
        print(f"{i}. Testing: '{test_case}'")
        result = analyze_complaint(test_case)
        
        if result and result.get('sections'):
            sections = result.get('sections', [])
            # Filter sections with confidence above threshold
            filtered_sections = [s for s in sections if s.get('confidence', 0) >= 0.3]
            # Sort by confidence (highest first) and take top 3
            filtered_sections = sorted(filtered_sections, key=lambda s: s.get('confidence', 0), reverse=True)[:3]
            
            if filtered_sections:
                print(f"   Found {len(filtered_sections)} relevant sections:")
                for section in filtered_sections:
                    confidence = section.get('confidence', 0)
                    print(f"   - Section {section['section_code']}: {section['section_name']} (Confidence: {confidence:.2%})")
            else:
                print("   No relevant sections found with confidence >= 30%")
        else:
            print("   No sections found")
        print()
