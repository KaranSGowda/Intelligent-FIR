"""
Script to train the ML model with new test cases.
"""

import os
import sys
import logging
from datetime import datetime

# Set environment variables for Flask
os.environ["FLASK_APP"] = "app.py"
os.environ["FLASK_ENV"] = "development"
os.environ["DATABASE_URL"] = "sqlite:///fir_system.db"

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler(sys.stdout)])

logger = logging.getLogger(__name__)

def train_model_with_new_cases():
    """Train the ML model with new test cases."""
    try:
        # Import Flask app and create application context
        from app import create_app
        app = create_app()

        # Use app context for database operations
        with app.app_context():
            # Import the ML analyzer and training data
            from utils.ml_analyzer import train_model
            from utils.training_data import TRAINING_DATA
            from new_training_cases import NEW_TRAINING_CASES

            # Combine existing training data with new cases
            combined_training_data = TRAINING_DATA + NEW_TRAINING_CASES
            
            # Log the number of training examples
            logger.info(f"Original training examples: {len(TRAINING_DATA)}")
            logger.info(f"New training examples: {len(NEW_TRAINING_CASES)}")
            logger.info(f"Total training examples: {len(combined_training_data)}")
            
            # Count short and long descriptions
            short_descriptions = [case for case in combined_training_data if len(case[0].split()) <= 20]
            long_descriptions = [case for case in combined_training_data if len(case[0].split()) > 20]
            
            logger.info(f"Short descriptions (≤20 words): {len(short_descriptions)}")
            logger.info(f"Long descriptions (>20 words): {len(long_descriptions)}")
            
            # Count unique IPC sections
            all_sections = set()
            for _, sections in combined_training_data:
                all_sections.update(sections)
            
            logger.info(f"Unique IPC sections in training data: {len(all_sections)}")
            logger.info(f"IPC sections: {', '.join(sorted(all_sections))}")
            
            # Train the model with combined data
            logger.info("Training model with combined data...")
            success = train_model(combined_training_data)
            
            if success:
                logger.info("Model training completed successfully!")
                
                # Save the final list of training cases
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = f"training_cases_{timestamp}.txt"
                
                with open(output_file, 'w') as f:
                    f.write("# Final List of Training Cases\n\n")
                    f.write(f"Total Cases: {len(combined_training_data)}\n")
                    f.write(f"Short Descriptions: {len(short_descriptions)}\n")
                    f.write(f"Long Descriptions: {len(long_descriptions)}\n")
                    f.write(f"Unique IPC Sections: {len(all_sections)}\n\n")
                    
                    f.write("## Short Descriptions\n\n")
                    for i, (text, sections) in enumerate(short_descriptions, 1):
                        f.write(f"{i}. \"{text}\" - Sections: {', '.join(sections)}\n")
                    
                    f.write("\n## Long Descriptions\n\n")
                    for i, (text, sections) in enumerate(long_descriptions, 1):
                        # Truncate long descriptions for readability
                        if len(text) > 100:
                            display_text = text[:100] + "..."
                        else:
                            display_text = text
                        f.write(f"{i}. \"{display_text}\" - Sections: {', '.join(sections)}\n")
                
                logger.info(f"Final list of training cases saved to {output_file}")
                return True
            else:
                logger.error("Model training failed!")
                return False
    
    except Exception as e:
        logger.error(f"Error training model with new cases: {str(e)}")
        return False

if __name__ == "__main__":
    train_model_with_new_cases()
