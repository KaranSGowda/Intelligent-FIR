"""
Script to test the comprehensively trained model with diverse examples.
"""

import os
import sys
import logging

# Set environment variables for Flask
os.environ["FLASK_APP"] = "app.py"
os.environ["FLASK_ENV"] = "development"
os.environ["DATABASE_URL"] = "sqlite:///fir_system.db"

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler(sys.stdout)])

logger = logging.getLogger(__name__)

# Test cases covering various IPC sections
TEST_CASES = [
    # Common crimes with standard descriptions
    "Someone stole my phone while I was on the bus",
    "My neighbor threatened to harm me if I don't stop complaining about the noise",
    "I was assaulted by a group of people outside a restaurant",
    "The accused forged my signature on bank documents",
    
    # Crimes with misspellings
    "I mudered a person in a fit of rage",
    "Someone was murderd yesterday near my house",
    "He stabed me with a knife during an argument",
    "I was asaulted by my neighbor last night",
    "Someone is harrasing me online and sending threatening messages",
    
    # Complex cases with multiple potential sections
    """I had invested Rs. 2,00,000 in a company based on the accused's promise of high returns. 
    After six months, when I asked for my money back, he kept making excuses and eventually 
    stopped responding to my calls. I later found out that the company was fake and many others 
    had been cheated in the same way.""",
    
    """The accused has been stalking me for the past month. He follows me to work, waits outside 
    my house, and sends me unwanted messages despite my clear refusal. Yesterday, he approached me 
    in a public place and made obscene gestures, causing me significant distress.""",
    
    """My husband and his family have been harassing me for additional dowry since our marriage 
    three years ago. They have physically assaulted me multiple times and threatened to throw me 
    out of the house if my parents don't give them more money and a car.""",
    
    """A group of five people broke into my shop at night by breaking the lock. They stole cash 
    and merchandise worth approximately Rs. 3,00,000. The incident was captured on CCTV camera.""",
    
    """The accused, who is a public servant, demanded a bribe of Rs. 10,000 to process my application. 
    When I refused, he threatened to reject my application and cause problems for me in the future."""
]

def test_model():
    """Test the trained model with diverse examples."""
    try:
        # Import Flask app and create application context
        from app import create_app
        app = create_app()

        # Use app context for database operations
        with app.app_context():
            # Import the ML analyzer
            from utils.ml_analyzer import predict_ipc_sections
            
            print("\n===== TESTING COMPREHENSIVELY TRAINED MODEL =====\n")
            
            for i, test_case in enumerate(TEST_CASES, 1):
                print(f"Test Case #{i}:")
                print(f"Description: {test_case[:100]}{'...' if len(test_case) > 100 else ''}")
                
                # Predict IPC sections
                results = predict_ipc_sections(test_case)
                
                print("\nPredicted IPC Sections:")
                for result in results:
                    print(f"- Section {result['section_code']}: {result['section_name']} (Confidence: {result['confidence']:.2f})")
                    print(f"  Relevance: {result['relevance']}")
                    print(f"  Keywords matched: {', '.join(result['keywords_matched']) if result['keywords_matched'] else 'None'}")
                
                print("\n" + "="*50 + "\n")
            
            return True
    
    except Exception as e:
        logger.error(f"Error testing model: {str(e)}")
        return False

if __name__ == "__main__":
    test_model()
