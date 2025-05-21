"""
Script to update the ML model to include all IPC sections from the database.
"""

import os
import re
import pickle
from app import app
from models import LegalSection
from utils.ml_analyzer import IPC_KEYWORDS, train_model

def get_keywords_for_section(section):
    """
    Generate keywords for a section based on its name and description.

    Args:
        section: LegalSection object

    Returns:
        list: List of keywords
    """
    keywords = []

    # Add the section name as keywords
    if section.name:
        # Split the name into words
        name_words = re.findall(r'\b\w+\b', section.name.lower())
        # Add individual words and combinations
        keywords.extend(name_words)
        if len(name_words) > 1:
            keywords.append(' '.join(name_words))

    # Add the description as keywords
    if section.description:
        # Extract key phrases from description
        # Look for phrases with these patterns:
        # - Verbs followed by objects
        # - Adjectives followed by nouns
        # - Common legal terms
        desc_lower = section.description.lower()

        # Extract common legal terms
        legal_terms = [
            "assault", "attack", "murder", "kill", "death", "injury", "hurt", "damage",
            "theft", "steal", "robbery", "burglary", "property", "cheating", "fraud",
            "criminal", "illegal", "unlawful", "offense", "crime", "victim", "accused",
            "rape", "sexual", "kidnap", "abduct", "threat", "intimidation", "extortion",
            "forgery", "document", "counterfeit", "fake", "false", "defamation", "insult",
            "trespass", "breach", "trust", "misappropriation", "embezzlement", "corruption",
            "bribe", "public servant", "government", "official", "negligence", "rash",
            "dowry", "cruelty", "harassment", "woman", "modesty", "obscene", "indecent"
        ]

        for term in legal_terms:
            if term in desc_lower:
                keywords.append(term)

                # Find surrounding context for better phrases
                match = re.search(r'\b\w+\s+' + re.escape(term) + r'\s+\w+\b', desc_lower)
                if match:
                    keywords.append(match.group(0))

                match = re.search(r'\b' + re.escape(term) + r'\s+\w+\b', desc_lower)
                if match:
                    keywords.append(match.group(0))

                match = re.search(r'\b\w+\s+' + re.escape(term) + r'\b', desc_lower)
                if match:
                    keywords.append(match.group(0))

    # Remove duplicates and empty strings
    keywords = list(set([k for k in keywords if k]))

    # If we couldn't generate any keywords, use some generic ones based on section code
    if not keywords:
        keywords = [f"section {section.code}", f"ipc {section.code}", f"offense under section {section.code}"]

    return keywords

def generate_example_for_section(section):
    """
    Generate a training example for a section.

    Args:
        section: LegalSection object

    Returns:
        tuple: (example_text, [section_code])
    """
    # Base templates for different types of sections
    templates = [
        "The accused {verb} the victim, which is an offense under section {code}.",
        "The complainant reported that the accused {verb}, violating section {code}.",
        "A case was filed against the accused for {verb_ing} the victim under section {code}.",
        "The victim alleged that the accused {verb}, which falls under section {code}.",
        "The accused was charged with {verb_ing} under section {code}."
    ]

    # Get appropriate verb based on section name/description
    verb = "committed an offense against"
    verb_ing = "committing an offense against"

    # Try to extract a more specific verb from section name or keywords
    if section.name:
        name_lower = section.name.lower()

        # Check for common offense types in the name
        if any(term in name_lower for term in ["murder", "homicide", "kill"]):
            verb = "killed"
            verb_ing = "killing"
        elif any(term in name_lower for term in ["hurt", "injury", "assault"]):
            verb = "assaulted"
            verb_ing = "assaulting"
        elif any(term in name_lower for term in ["theft", "steal"]):
            verb = "stole property from"
            verb_ing = "stealing property from"
        elif any(term in name_lower for term in ["rape", "sexual"]):
            verb = "sexually assaulted"
            verb_ing = "sexually assaulting"
        elif any(term in name_lower for term in ["cheat", "fraud"]):
            verb = "defrauded"
            verb_ing = "defrauding"
        elif any(term in name_lower for term in ["threat", "intimidation"]):
            verb = "threatened"
            verb_ing = "threatening"
        elif any(term in name_lower for term in ["trespass"]):
            verb = "trespassed on the property of"
            verb_ing = "trespassing on the property of"
        elif any(term in name_lower for term in ["forgery", "document"]):
            verb = "forged documents of"
            verb_ing = "forging documents of"
        elif any(term in name_lower for term in ["kidnap", "abduct"]):
            verb = "kidnapped"
            verb_ing = "kidnapping"
        elif any(term in name_lower for term in ["defamation", "insult"]):
            verb = "defamed"
            verb_ing = "defaming"

    # Select a template and fill it
    import random
    template = random.choice(templates)
    example = template.format(
        code=section.code,
        verb=verb,
        verb_ing=verb_ing
    )

    return (example, [section.code])

def update_ipc_keywords():
    """Update the IPC_KEYWORDS dictionary with all sections from the database."""
    with app.app_context():
        # Get all sections from database
        db_sections = LegalSection.query.all()

        # Create a copy of the current IPC_KEYWORDS
        updated_keywords = dict(IPC_KEYWORDS)

        # Count how many sections we're adding
        new_sections_count = 0

        # Add missing sections
        for section in db_sections:
            if section.code not in updated_keywords:
                # Generate keywords for this section
                keywords = get_keywords_for_section(section)

                # Add to the dictionary
                updated_keywords[section.code] = keywords
                new_sections_count += 1
                print(f"Added section {section.code}: {section.name} with {len(keywords)} keywords")

        # Save the updated keywords to a separate file instead of modifying the source code
        # This is safer and more maintainable
        keywords_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'utils', 'updated_ipc_keywords.py')

        with open(keywords_path, 'w') as f:
            f.write("# Updated IPC keywords dictionary\n\n")
            f.write("IPC_KEYWORDS = {\n")
            for code, keywords in sorted(updated_keywords.items()):
                keywords_str = ", ".join([f"'{k}'" for k in keywords])
                f.write(f"    '{code}': [{keywords_str}],\n")
            f.write("}\n")

        print(f"Saved updated IPC_KEYWORDS dictionary to {keywords_path}")
        print(f"Added {new_sections_count} new sections.")
        print(f"Total sections in updated dictionary: {len(updated_keywords)}")

        return updated_keywords

def generate_training_data():
    """Generate training examples for all IPC sections in the database."""
    with app.app_context():
        # Get all sections from database
        db_sections = LegalSection.query.all()

        # Generate examples
        training_data = []

        # First, include the existing training data from the model
        # This ensures we don't lose the quality examples we already have
        existing_data = [
            # Section 302 - Murder
            ("The accused murdered the victim by stabbing him multiple times.", ["302"]),
            ("The victim was killed by the accused with a knife.", ["302"]),
            ("The accused shot and killed the victim during an argument.", ["302"]),
            ("The accused strangled the victim to death.", ["302"]),
            ("The victim died due to poisoning administered by the accused.", ["302"]),
            ("The accused hit the victim on the head with a heavy object causing death.", ["302"]),
            ("The accused deliberately ran over the victim with a car, killing them instantly.", ["302"]),

            # Section 307 - Attempt to Murder
            ("The accused attempted to kill the victim by firing a gun.", ["307"]),
            ("The accused tried to stab the victim but was stopped.", ["307"]),
            ("The accused poisoned the food but the victim survived after hospital treatment.", ["307"]),
            ("The accused pushed the victim from a height with intent to kill, but the victim survived.", ["307"]),
            ("The accused attacked the victim with a deadly weapon but failed to kill them.", ["307"]),
            ("The accused tried to strangle the victim but was interrupted.", ["307"]),

            # Section 323 - Voluntarily causing hurt
            ("The accused assaulted the victim causing injuries.", ["323"]),
            ("The accused slapped and punched the victim.", ["323"]),
            ("The accused beat the victim with bare hands.", ["323"]),
            ("The victim was physically assaulted by the accused.", ["323"]),
            ("The accused pushed the victim causing them to fall and get injured.", ["323"]),

            # Section 376 - Rape
            ("The accused sexually assaulted the victim.", ["376"]),
            ("The accused raped the victim at his residence.", ["376"]),
            ("The victim was sexually violated by the accused against her consent.", ["376"]),
            ("The accused committed sexual intercourse with the victim without consent.", ["376"]),

            # Section 420 - Cheating
            ("The accused cheated the victim by selling fake property documents.", ["420"]),
            ("The accused fraudulently took money promising a job that didn't exist.", ["420"]),
            ("The victim was deceived into investing in a fake company by the accused.", ["420"]),
            ("The accused sold counterfeit products claiming them to be genuine.", ["420"]),
            ("The accused ran a Ponzi scheme defrauding multiple victims.", ["420"]),
        ]

        training_data.extend(existing_data)
        print(f"Added {len(existing_data)} existing high-quality examples.")

        # Keep track of sections we've already covered
        covered_sections = set([code for _, codes in existing_data for code in codes])

        # Generate examples for remaining sections
        for section in db_sections:
            if section.code not in covered_sections:
                # Generate 2 examples for each section
                for _ in range(2):
                    example = generate_example_for_section(section)
                    training_data.append(example)
                covered_sections.add(section.code)
                print(f"Generated examples for section {section.code}: {section.name}")

        # Save the training data to a file for future use
        training_data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'utils', 'training_data.py')

        with open(training_data_path, 'w') as f:
            f.write("# Training data for IPC sections\n\n")
            f.write("TRAINING_DATA = [\n")
            for text, codes in training_data:
                codes_str = ", ".join([f"'{code}'" for code in codes])
                f.write(f"    (\"{text}\", [{codes_str}]),\n")
            f.write("]\n")

        print(f"Generated {len(training_data)} training examples for {len(covered_sections)} sections.")
        print(f"Saved training data to {training_data_path}")

        return training_data

def retrain_model(training_data):
    """Retrain the model with the expanded dataset."""
    with app.app_context():
        print("Retraining model with expanded dataset...")
        success = train_model(training_data)
        if success:
            print("Model successfully retrained.")
        else:
            print("Failed to retrain model.")

if __name__ == "__main__":
    try:
        print("=== Step 1: Updating IPC_KEYWORDS dictionary ===")
        updated_keywords = update_ipc_keywords()
        print("\n=== Step 2: Generating training data for all sections ===")
        training_data = generate_training_data()
        print("\n=== Step 3: Retraining the model with expanded dataset ===")
        retrain_model(training_data)
        print("\n=== Process completed successfully! ===")
        print("Your model now includes all IPC sections from the database.")
        print("To use the updated model, you need to:")
        print("1. Copy utils/updated_ipc_keywords.py to utils/ml_analyzer.py (replacing the IPC_KEYWORDS dictionary)")
        print("2. Restart the application")
    except Exception as e:
        import traceback
        print(f"\n=== ERROR: {str(e)} ===")
        print(traceback.format_exc())
        print("\nThe process did not complete successfully. Please check the error message above.")
