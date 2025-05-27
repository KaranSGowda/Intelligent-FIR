from app import create_app
from models import LegalSection

app = create_app()

with app.app_context():
    # Get the first 10 sections ordered by code
    sections = LegalSection.query.order_by(LegalSection.code).limit(10).all()
    print('First 10 IPC sections:')
    for section in sections:
        print(f'Section {section.code}: {section.name}')

    # Get the total count
    total = LegalSection.query.count()
    print(f'\nTotal IPC sections: {total}')

    # Get the minimum and maximum section codes
    min_section = LegalSection.query.order_by(LegalSection.code).first()
    max_section = LegalSection.query.order_by(LegalSection.code.desc()).first()

    if min_section and max_section:
        print(f'Section code range: {min_section.code} to {max_section.code}')

    # Check if there are any sections with codes less than 100
    low_sections = LegalSection.query.filter(LegalSection.code < '100').all()
    print(f'\nSections with code < 100: {len(low_sections)}')
    for section in low_sections:
        print(f'Section {section.code}: {section.name}')
