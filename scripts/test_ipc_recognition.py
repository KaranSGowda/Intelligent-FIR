"""Script to test the chatbot's ability to recognize IPC sections.

This script tests the chatbot's ability to recognize and respond to queries about
IPC sections after training with the comprehensive dataset.
"""

import os
import sys
import logging
import random

# Add the parent directory to the path so we can import the app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler(sys.stdout)])

logger = logging.getLogger(__name__)

def test_section_recognition():
    """Test the chatbot's ability to recognize IPC sections."""
    try:
        from app import create_app
        from models import LegalSection
        from utils.chatbot import FIRChatbot
        
        app = create_app()
        
        with app.app_context():
            # Initialize the chatbot
            chatbot = FIRChatbot()
            
            # Get all IPC sections from the database
            sections = LegalSection.query.order_by(LegalSection.code).all()
            
            # Select a random sample of sections to test (max 20)
            sample_size = min(20, len(sections))
            sample_sections = random.sample(sections, sample_size)
            
            logger.info(f"Testing recognition of {sample_size} random IPC sections")
            
            # Test direct queries about sections
            success_count = 0
            for section in sample_sections:
                # Generate a query about this section
                query = f"What is IPC section {section.code}?"
                
                # Process the query
                response = chatbot.process_query(query)
                
                # Check if the response contains the section code
                if section.code in response:
                    success_count += 1
                    logger.info(f"✓ Successfully recognized section {section.code}")
                else:
                    logger.warning(f"✗ Failed to recognize section {section.code}")
                    logger.warning(f"Query: {query}")
                    logger.warning(f"Response: {response[:100]}...")
            
            # Calculate success rate
            success_rate = (success_count / sample_size) * 100
            logger.info(f"Recognition success rate: {success_rate:.2f}%")
            
            # Test more complex queries
            complex_queries = [
                "What are the common IPC sections for theft?",
                "Tell me about sections related to murder",
                "What IPC sections apply to assault?",
                "Explain the punishment under section 302",
                "When does section 376 apply?"
            ]
            
            logger.info("\nTesting complex queries:")
            for query in complex_queries:
                response = chatbot.process_query(query)
                logger.info(f"Query: {query}")
                logger.info(f"Response: {response[:100]}...\n")
            
            return success_rate >= 80  # Consider it successful if at least 80% of sections are recognized
    
    except Exception as e:
        logger.error(f"Error testing section recognition: {str(e)}")
        return False

def test_complaint_analysis():
    """Test the chatbot's ability to analyze complaints and identify applicable IPC sections."""
    try:
        from app import create_app
        from utils.chatbot import FIRChatbot
        
        app = create_app()
        
        with app.app_context():
            # Initialize the chatbot
            chatbot = FIRChatbot()
            
            # Test cases for complaint analysis
            test_cases = [
                "My phone was stolen from my pocket while I was on the bus",
                "Someone broke into my house and stole valuables",
                "I was assaulted by a group of people yesterday",
                "The accused threatened to kill me if I didn't pay him money",
                "My neighbor has been harassing me and making false accusations"
            ]
            
            logger.info("\nTesting complaint analysis:")
            for case in test_cases:
                # Create a query for analysis
                query = f"Analyze this complaint: {case}"
                
                # Process the query
                response = chatbot.process_query(query)
                
                logger.info(f"Complaint: {case}")
                logger.info(f"Response: {response[:200]}...\n")
            
            return True
    
    except Exception as e:
        logger.error(f"Error testing complaint analysis: {str(e)}")
        return False

def main():
    """Main function to run the script."""
    logger.info("Testing chatbot's ability to recognize IPC sections...")
    
    # Test section recognition
    if test_section_recognition():
        logger.info("Section recognition test passed!")
    else:
        logger.warning("Section recognition test failed")
    
    # Test complaint analysis
    if test_complaint_analysis():
        logger.info("Complaint analysis test completed")
    else:
        logger.warning("Complaint analysis test failed")

if __name__ == "__main__":
    main()