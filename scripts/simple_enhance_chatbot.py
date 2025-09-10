"""Simple script to enhance the chatbot's IPC section recognition.

This script updates the chatbot.py file to use the enhanced IPC patterns
from the ipc_patterns.py module.
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
    from utils import ipc_patterns
    logger.info("Successfully imported chatbot and ipc_patterns modules")
except ImportError as e:
    logger.error(f"Error importing modules: {e}")
    sys.exit(1)

def enhance_chatbot():
    """Enhance the chatbot with improved IPC section recognition."""
    try:
        # Check if FIRChatbot class exists in the chatbot module
        if not hasattr(chatbot, 'FIRChatbot'):
            logger.error("FIRChatbot class not found in chatbot module")
            return False
        
        # Add the is_ipc_section_query method to the FIRChatbot class
        chatbot.FIRChatbot._is_ipc_section_query = ipc_patterns.is_ipc_section_query
        
        # Add the process_ipc_query method to the FIRChatbot class
        chatbot.FIRChatbot._process_ipc_query = ipc_patterns.process_ipc_query
        
        # Modify the process_query method to use the new IPC section recognition
        original_process_query = chatbot.FIRChatbot.process_query
        
        def enhanced_process_query(self, query):
            # First check if it's an IPC section query
            ipc_response = self._process_ipc_query(query)
            if ipc_response:
                return ipc_response
            
            # If not, use the original process_query method
            return original_process_query(self, query)
        
        # Replace the original process_query method with the enhanced one
        chatbot.FIRChatbot.process_query = enhanced_process_query
        
        logger.info("Successfully enhanced chatbot with improved IPC section recognition")
        return True
    
    except Exception as e:
        logger.error(f"Error enhancing chatbot: {e}")
        return False

def main():
    """Main function."""
    logger.info("Enhancing chatbot with improved IPC section recognition...")
    
    if enhance_chatbot():
        logger.info("Successfully enhanced chatbot with improved IPC section recognition")
    else:
        logger.error("Failed to enhance chatbot")

if __name__ == "__main__":
    main()