from app import create_app
from models import LegalSection
from utils.legal_mapper import initialize_legal_sections

app = create_app()

with app.app_context():
    # Delete all existing legal sections
    print("Deleting existing legal sections...")
    LegalSection.query.delete()
    
    # Initialize legal sections
    print("Initializing legal sections...")
    initialize_legal_sections()
    
    # Count the legal sections
    count = LegalSection.query.count()
    print(f"Total legal sections: {count}")
    
    # Get the minimum and maximum section codes
    min_section = LegalSection.query.order_by(LegalSection.code).first()
    max_section = LegalSection.query.order_by(LegalSection.code.desc()).first()
    
    if min_section and max_section:
        print(f"Section code range: {min_section.code} to {max_section.code}")
    
    # Check if there are any sections with codes less than 100
    low_sections = LegalSection.query.filter(LegalSection.code < '100').all()
    print(f"Sections with code < 100: {len(low_sections)}")
    
    # Print the first 5 sections
    print("\nFirst 5 sections:")
    sections = LegalSection.query.order_by(LegalSection.code).limit(5).all()
    for section in sections:
        print(f"Section {section.code}: {section.name}")
