"""
Script to train the ML model with comprehensive IPC section coverage.
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

def train_comprehensive_model():
    """Train the ML model with comprehensive IPC section coverage."""
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
            from comprehensive_ipc_training import ALL_TRAINING_CASES, MAJOR_IPC_SECTIONS
            
            # Combine all training data
            combined_training_data = TRAINING_DATA + NEW_TRAINING_CASES + ALL_TRAINING_CASES
            
            # Log the number of training examples
            logger.info(f"Original training examples: {len(TRAINING_DATA)}")
            logger.info(f"New training examples: {len(NEW_TRAINING_CASES)}")
            logger.info(f"Comprehensive training examples: {len(ALL_TRAINING_CASES)}")
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
            logger.info(f"Major IPC sections targeted: {len(MAJOR_IPC_SECTIONS)}")
            
            # Calculate coverage of major sections
            covered_major_sections = set(all_sections).intersection(set(MAJOR_IPC_SECTIONS))
            coverage_percentage = (len(covered_major_sections) / len(MAJOR_IPC_SECTIONS)) * 100
            
            logger.info(f"Major IPC sections covered: {len(covered_major_sections)} ({coverage_percentage:.2f}%)")
            
            # Train the model with combined data
            logger.info("Training model with combined data...")
            success = train_model(combined_training_data)
            
            if success:
                logger.info("Model training completed successfully!")
                
                # Save the final list of training cases
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = f"comprehensive_training_cases_{timestamp}.txt"
                
                with open(output_file, 'w') as f:
                    f.write("# Comprehensive List of Training Cases\n\n")
                    f.write(f"Total Cases: {len(combined_training_data)}\n")
                    f.write(f"Short Descriptions: {len(short_descriptions)}\n")
                    f.write(f"Long Descriptions: {len(long_descriptions)}\n")
                    f.write(f"Unique IPC Sections: {len(all_sections)}\n")
                    f.write(f"Major IPC Sections Coverage: {len(covered_major_sections)}/{len(MAJOR_IPC_SECTIONS)} ({coverage_percentage:.2f}%)\n\n")
                    
                    f.write("## IPC Sections Covered\n\n")
                    for section in sorted(all_sections):
                        f.write(f"- Section {section}\n")
                    
                    f.write("\n## Sample Training Cases\n\n")
                    # Write a sample of training cases (to keep the file manageable)
                    sample_size = min(50, len(combined_training_data))
                    for i, (text, sections) in enumerate(combined_training_data[:sample_size], 1):
                        # Truncate long descriptions for readability
                        if len(text) > 100:
                            display_text = text[:100] + "..."
                        else:
                            display_text = text
                        f.write(f"{i}. \"{display_text}\" - Sections: {', '.join(sections)}\n")
                    
                    if len(combined_training_data) > sample_size:
                        f.write(f"\n... and {len(combined_training_data) - sample_size} more cases\n")
                
                logger.info(f"Comprehensive list of training cases saved to {output_file}")
                return True
            else:
                logger.error("Model training failed!")
                return False
    
    except Exception as e:
        logger.error(f"Error training model with comprehensive coverage: {str(e)}")
        return False

if __name__ == "__main__":
    train_comprehensive_model()
