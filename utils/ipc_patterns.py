"""Enhanced patterns for IPC section recognition in the chatbot.

This module provides enhanced regex patterns and utility functions for recognizing
IPC section queries in the chatbot.
"""

# Common IPC sections with their codes, names, and descriptions
COMMON_IPC_SECTIONS = [
    {
        'code': '302',
        'name': 'Punishment for murder',
        'description': 'Whoever commits murder shall be punished with death, or imprisonment for life, and shall also be liable to fine.'
    },
    {
        'code': '304B',
        'name': 'Dowry death',
        'description': 'Where the death of a woman is caused by any burns or bodily injury or occurs otherwise than under normal circumstances within seven years of her marriage.'
    },
    {
        'code': '354',
        'name': 'Assault or criminal force to woman with intent to outrage her modesty',
        'description': 'Whoever assaults or uses criminal force to any woman, intending to outrage or knowing it to be likely that he will thereby outrage her modesty.'
    },
    {
        'code': '376',
        'name': 'Punishment for rape',
        'description': 'Whoever commits rape shall be punished with imprisonment of either description for a term which shall not be less than seven years.'
    },
    {
        'code': '420',
        'name': 'Cheating and dishonestly inducing delivery of property',
        'description': 'Whoever cheats and thereby dishonestly induces the person deceived to deliver any property to any person.'
    },
    {
        'code': '498A',
        'name': 'Husband or relative of husband of a woman subjecting her to cruelty',
        'description': 'Whoever, being the husband or the relative of the husband of a woman, subjects such woman to cruelty.'
    },
    {
        'code': '509',
        'name': 'Word, gesture or act intended to insult the modesty of a woman',
        'description': 'Whoever, intending to insult the modesty of any woman, utters any word, makes any sound or gesture, or exhibits any object.'
    },
    {
        'code': '323',
        'name': 'Punishment for voluntarily causing hurt',
        'description': 'Whoever voluntarily causes hurt shall be punished with imprisonment of either description for a term which may extend to one year, or with fine which may extend to one thousand rupees, or with both.'
    },
    {
        'code': '379',
        'name': 'Punishment for theft',
        'description': 'Whoever commits theft shall be punished with imprisonment of either description for a term which may extend to three years, or with fine, or with both.'
    },
    {
        'code': '506',
        'name': 'Punishment for criminal intimidation',
        'description': 'Whoever commits the offence of criminal intimidation shall be punished with imprisonment of either description for a term which may extend to two years, or with fine, or with both.'
    },
]

# Enhanced regex patterns for IPC section recognition
DIRECT_SECTION_PATTERN = r"(?i)(?:what|tell|explain|describe)\s+(?:is|about|does)?\s+(?:the)?\s*(?:ipc|indian\s+penal\s+code)\s*(?:section)?\s*([0-9]+[A-Za-z]*)\s*(?:\?|$)"

# Pattern for general IPC section queries
GENERAL_IPC_PATTERN = r"(?i)(?:what|list|tell|show)\s+(?:are|me|about)\s+(?:the)?\s*(?:common|important|all)?\s*(?:ipc|indian\s+penal\s+code)\s*(?:sections|laws)\s*(?:\?|$)"

# Function to check if a query is about an IPC section
def is_ipc_section_query(query):
    """Check if the query is about an IPC section.
    
    Args:
        query: The user query
        
    Returns:
        tuple: (is_ipc_query, section_code)
    """
    import re
    
    # Check for direct section queries
    direct_match = re.search(DIRECT_SECTION_PATTERN, query)
    if direct_match:
        return True, direct_match.group(1)
    
    # Check for section name queries
    for section in COMMON_IPC_SECTIONS:
        # Extract keywords from section name
        keywords = section['name'].lower().split()
        keywords = [keyword for keyword in keywords if len(keyword) > 3]  # Only use keywords with more than 3 characters
        
        # Check if any keyword is in the query
        if any(keyword in query.lower() for keyword in keywords):
            return True, section['code']
    
    # Check for general IPC queries
    if re.search(GENERAL_IPC_PATTERN, query):
        return True, None
    
    return False, None

# Function to get information about an IPC section
def get_section_info(section_code):
    """Get information about an IPC section.
    
    Args:
        section_code: The IPC section code
        
    Returns:
        dict: Section information or None if not found
    """
    for section in COMMON_IPC_SECTIONS:
        if section['code'] == section_code:
            return section
    
    return None

# Function to list common IPC sections
def list_common_sections():
    """List common IPC sections.
    
    Returns:
        str: Formatted list of common IPC sections
    """
    response = "Here are some common IPC sections:\n\n"
    
    for section in COMMON_IPC_SECTIONS:
        response += f"- Section {section['code']}: {section['name']}\n"
    
    return response

# Function to process an IPC section query
def process_ipc_query(query):
    """Process an IPC section query and return a response.
    
    Args:
        query: The user query
        
    Returns:
        str: Response to the query
    """
    is_ipc_query, section_code = is_ipc_section_query(query)
    
    if is_ipc_query:
        if section_code:
            # Query about a specific section
            section = get_section_info(section_code)
            
            if section:
                return f"Section {section['code']} of IPC deals with {section['name']}. {section['description']}"
            else:
                return f"I recognize that you're asking about IPC section {section_code}, but I don't have detailed information about it."
        else:
            # General query about IPC sections
            return list_common_sections()
    
    return None  # Not an IPC query