"""Simple test script for the enhanced chatbot's IPC section recognition.

This script tests the chatbot's ability to recognize and respond to
queries about IPC sections using the enhanced patterns.
"""

import os
import sys
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the chatbot module
try:
    from utils import chatbot
    logger.info("Successfully imported chatbot module")
except ImportError as e:
    logger.error(f"Error importing chatbot module: {e}")
    sys.exit(1)

def test_direct_section_queries():
    """Test direct queries about specific IPC sections."""
    logger.info("Testing direct section queries...")
    
    # Create a chatbot instance
    bot = chatbot.FIRChatbot()
    
    # Test queries
    test_queries = [
        "What is IPC section 302?",
        "Tell me about section 376 of IPC",
        "Explain IPC 498A",
        "What does Indian Penal Code section 420 cover?",
        "IPC 354?"
    ]
    
    success_count = 0
    
    for query in test_queries:
        logger.info(f"Testing query: {query}")
        response = bot.process_query(query)
        
        # Check if response is a dictionary (the expected format)
        if isinstance(response, dict) and 'text' in response:
            response_text = response['text']
            if "section" in response_text.lower():
                logger.info("✓ Successfully recognized as IPC section query")
                logger.info(f"Response: {response_text[:100]}..." if len(response_text) > 100 else f"Response: {response_text}")
                success_count += 1
            else:
                logger.error("✗ Failed to recognize as IPC section query")
                logger.error(f"Response: {response_text[:100]}..." if len(response_text) > 100 else f"Response: {response_text}")
        else:
            logger.error("✗ Failed to get proper response format")
            logger.error(f"Response: {response}")
    
    success_rate = (success_count / len(test_queries)) * 100
    logger.info(f"Direct section query success rate: {success_rate:.2f}%")
    
    return success_rate

def test_section_name_queries():
    """Test queries about IPC sections by their names."""
    logger.info("Testing section name queries...")
    
    # Create a chatbot instance
    bot = chatbot.FIRChatbot()
    
    # Test queries
    test_queries = [
        "What is the punishment for murder?",
        "Tell me about dowry death",
        "What does the law say about cheating?",
        "Explain the section on rape",
        "What is criminal intimidation?"
    ]
    
    success_count = 0
    
    for query in test_queries:
        logger.info(f"Testing query: {query}")
        response = bot.process_query(query)
        
        # Check if response is a dictionary (the expected format)
        if isinstance(response, dict) and 'text' in response:
            response_text = response['text']
            if "section" in response_text.lower():
                logger.info("✓ Successfully recognized as IPC section query")
                logger.info(f"Response: {response_text[:100]}..." if len(response_text) > 100 else f"Response: {response_text}")
                success_count += 1
            else:
                logger.error("✗ Failed to recognize as IPC section query")
                logger.error(f"Response: {response_text[:100]}..." if len(response_text) > 100 else f"Response: {response_text}")
        else:
            logger.error("✗ Failed to get proper response format")
            logger.error(f"Response: {response}")
    
    success_rate = (success_count / len(test_queries)) * 100
    logger.info(f"Section name query success rate: {success_rate:.2f}%")
    
    return success_rate

def test_general_ipc_queries():
    """Test general queries about IPC sections."""
    logger.info("Testing general IPC queries...")
    
    # Create a chatbot instance
    bot = chatbot.FIRChatbot()
    
    # Test queries
    test_queries = [
        "What are the common IPC sections?",
        "List all IPC sections",
        "Tell me about Indian Penal Code sections",
        "Show me important IPC laws",
        "What IPC sections should I know about?"
    ]
    
    success_count = 0
    
    for query in test_queries:
        logger.info(f"Testing query: {query}")
        response = bot.process_query(query)
        
        # Check if response is a dictionary (the expected format)
        if isinstance(response, dict) and 'text' in response:
            response_text = response['text']
            if "section" in response_text.lower() and "common" in response_text.lower():
                logger.info("✓ Successfully recognized as general IPC query")
                logger.info(f"Response: {response_text[:100]}..." if len(response_text) > 100 else f"Response: {response_text}")
                success_count += 1
            else:
                logger.error("✗ Failed to recognize as general IPC query")
                logger.error(f"Response: {response_text[:100]}..." if len(response_text) > 100 else f"Response: {response_text}")
        else:
            logger.error("✗ Failed to get proper response format")
            logger.error(f"Response: {response}")
    
    success_rate = (success_count / len(test_queries)) * 100
    logger.info(f"General IPC query success rate: {success_rate:.2f}%")
    
    return success_rate

def main():
    """Main function."""
    logger.info("Testing chatbot's IPC section recognition...")
    
    # Test direct section queries
    direct_success_rate = test_direct_section_queries()
    
    # Test section name queries
    name_success_rate = test_section_name_queries()
    
    # Test general IPC queries
    general_success_rate = test_general_ipc_queries()
    
    # Calculate overall success rate
    overall_success_rate = (direct_success_rate + name_success_rate + general_success_rate) / 3
    
    logger.info("===== Test Results =====")
    logger.info(f"Direct section query success rate: {direct_success_rate:.2f}%")
    logger.info(f"Section name query success rate: {name_success_rate:.2f}%")
    logger.info(f"General IPC query success rate: {general_success_rate:.2f}%")
    logger.info(f"Overall success rate: {overall_success_rate:.2f}%")
    
    if overall_success_rate >= 80:
        logger.info("✓ Chatbot successfully trained to recognize IPC sections")
    else:
        logger.warning("⚠ Chatbot needs improvement in recognizing IPC sections")

if __name__ == "__main__":
    main()