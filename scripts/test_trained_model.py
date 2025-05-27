"""
Script to test the trained model with new examples.
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

# Test cases to evaluate the model
TEST_CASES = [
    # Short descriptions
    "Someone stole my phone while I was on the bus",
    "My neighbor threatened to harm me if I don't stop complaining about the noise",
    "I was assaulted by a group of people outside a restaurant",
    "The accused forged my signature on bank documents",
    
    # Long descriptions
    """I had invested Rs. 2,00,000 in a company based on the accused's promise of high returns. 
    After six months, when I asked for my money back, he kept making excuses and eventually 
    stopped responding to my calls. I later found out that the company was fake and many others 
    had been cheated in the same way.""",
    
    """The accused has been stalking me for the past month. He follows me to work, waits outside 
    my house, and sends me unwanted messages despite my clear refusal. Yesterday, he approached me 
    in a public place and made obscene gestures, causing me significant distress."""
]

def test_model():
    """Test the trained model with example cases."""
    try:
        # Import Flask app and create application context
        from app import create_app
        app = create_app()

        # Use app context for database operations
        with app.app_context():
            # Import the ML analyzer
            from utils.ml_analyzer import predict_ipc_sections
            
            print("\n===== TESTING TRAINED MODEL =====\n")
            
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
