"""
Script to count the number of IPC sections in the database and model.
"""

from app import app
from models import LegalSection
from utils.ml_analyzer import IPC_KEYWORDS

def count_sections():
    """Count the number of IPC sections in the database and model."""
    with app.app_context():
        # Count sections in database
        db_sections = LegalSection.query.all()
        db_section_count = len(db_sections)
        
        # Get unique section codes from database
        db_section_codes = sorted([section.code for section in db_sections])
        
        # Count sections in IPC_KEYWORDS dictionary
        model_section_count = len(IPC_KEYWORDS)
        model_section_codes = sorted(list(IPC_KEYWORDS.keys()))
        
        # Print results
        print(f"Total IPC sections in database: {db_section_count}")
        print(f"Total IPC sections in model: {model_section_count}")
        
        # Print section codes from database
        print("\nIPC sections in database:")
        print(", ".join(db_section_codes))
        
        # Print section codes from model
        print("\nIPC sections in model:")
        print(", ".join(model_section_codes))
        
        # Find sections in database but not in model
        db_only = set(db_section_codes) - set(model_section_codes)
        if db_only:
            print("\nSections in database but not in model:")
            print(", ".join(sorted(list(db_only))))
        
        # Find sections in model but not in database
        model_only = set(model_section_codes) - set(db_section_codes)
        if model_only:
            print("\nSections in model but not in database:")
            print(", ".join(sorted(list(model_only))))

if __name__ == "__main__":
    count_sections()
