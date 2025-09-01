"""
Plan to ensure complete coverage of all IPC sections in the training dataset.
This file outlines the approach and provides a script to generate training examples
for all IPC sections not currently covered.
"""

import os
import sys
import logging
import sqlite3
import json
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler(sys.stdout)])

logger = logging.getLogger(__name__)

# Set environment variables
os.environ["FLASK_APP"] = "app.py"
os.environ["FLASK_ENV"] = "development"
os.environ["DATABASE_URL"] = "sqlite:///fir_system.db"

def get_all_ipc_sections():
    """Get all IPC sections from the database."""
    try:
        # Connect to the database
        conn = sqlite3.connect('fir_system.db')
        cursor = conn.cursor()
        
        # Query all IPC sections
        cursor.execute("SELECT code, name, description FROM legal_sections ORDER BY code")
        sections = cursor.fetchall()
        
        # Close the connection
        conn.close()
        
        # Convert to dictionary for easier access
        sections_dict = {section[0]: {"name": section[1], "description": section[2]} for section in sections}
        
        logger.info(f"Retrieved {len(sections_dict)} IPC sections from the database")
        return sections_dict
    
    except Exception as e:
        logger.error(f"Error retrieving IPC sections: {str(e)}")
        return {}

def get_currently_covered_sections():
    """Get the IPC sections currently covered in the training data."""
    try:
        # Import the training data
        from utils.training_data import TRAINING_DATA
        from new_training_cases import NEW_TRAINING_CASES
        
        # Combine existing and new training data
        combined_training_data = TRAINING_DATA + NEW_TRAINING_CASES
        
        # Extract all sections
        covered_sections = set()
        for _, sections in combined_training_data:
            covered_sections.update(sections)
        
        logger.info(f"Currently covered sections: {len(covered_sections)}")
        return covered_sections
    
    except Exception as e:
        logger.error(f"Error getting currently covered sections: {str(e)}")
        return set()

def generate_training_examples(missing_sections, all_sections_dict):
    """Generate training examples for missing IPC sections."""
    training_examples = []
    
    for section_code in missing_sections:
        section_info = all_sections_dict.get(section_code, {})
        section_name = section_info.get("name", f"Section {section_code}")
        section_desc = section_info.get("description", "")
        
        # Generate a short description example
        short_desc = f"The accused violated section {section_code} by committing an offense related to {section_name}."
        
        # Generate a more detailed description
        detailed_desc = f"""
        On [DATE], the complainant reported that the accused committed an offense under section {section_code} 
        of the Indian Penal Code. The accused's actions constitute {section_name}, as defined in the IPC. 
        According to the complainant, the accused [SPECIFIC ACTION RELATED TO THE OFFENSE]. 
        This is a clear violation of section {section_code} which states: "{section_desc}".
        """
        
        # Add both examples to the training data
        training_examples.append((short_desc, [section_code]))
        training_examples.append((detailed_desc, [section_code]))
    
    logger.info(f"Generated {len(training_examples)} training examples for {len(missing_sections)} missing sections")
    return training_examples

def save_additional_training_data(training_examples):
    """Save the additional training examples to a file."""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"additional_training_cases_{timestamp}.py"
        
        with open(filename, 'w') as f:
            f.write('"""\n')
            f.write('Additional training cases to cover all IPC sections.\n')
            f.write('"""\n\n')
            f.write('# Additional training cases for complete IPC coverage\n')
            f.write('ADDITIONAL_TRAINING_CASES = [\n')
            
            for example in training_examples:
                text, sections = example
                # Format the text and sections for Python
                formatted_text = text.replace('\n', ' ').strip()
                formatted_sections = json.dumps(sections)
                f.write(f'    ("{formatted_text}", {formatted_sections}),\n')
            
            f.write(']\n')
        
        logger.info(f"Saved {len(training_examples)} training examples to {filename}")
        return filename
    
    except Exception as e:
        logger.error(f"Error saving additional training data: {str(e)}")
        return None

def main():
    """Main function to ensure complete IPC section coverage."""
    # Get all IPC sections from the database
    all_sections_dict = get_all_ipc_sections()
    all_sections = set(all_sections_dict.keys())
    
    # Get currently covered sections
    covered_sections = get_currently_covered_sections()
    
    # Identify missing sections
    missing_sections = all_sections - covered_sections
    
    logger.info(f"Total IPC sections: {len(all_sections)}")
    logger.info(f"Currently covered sections: {len(covered_sections)}")
    logger.info(f"Missing sections: {len(missing_sections)}")
    
    if missing_sections:
        # Generate training examples for missing sections
        training_examples = generate_training_examples(missing_sections, all_sections_dict)
        
        # Save the additional training data
        filename = save_additional_training_data(training_examples)
        
        if filename:
            logger.info(f"Successfully created additional training data in {filename}")
            logger.info("Run the following command to train the model with complete coverage:")
            logger.info(f"python train_with_complete_coverage.py")
        else:
            logger.error("Failed to create additional training data")
    else:
        logger.info("All IPC sections are already covered in the training data!")

if __name__ == "__main__":
    main()
