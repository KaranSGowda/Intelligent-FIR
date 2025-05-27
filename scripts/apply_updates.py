"""
Script to apply the updated IPC keywords to the ML analyzer module.
"""

import os
import re
import shutil

def apply_updates():
    """Apply the updated IPC keywords to the ML analyzer module."""
    # Paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    ml_analyzer_path = os.path.join(base_dir, 'utils', 'ml_analyzer.py')
    updated_keywords_path = os.path.join(base_dir, 'utils', 'updated_ipc_keywords.py')
    
    # Check if files exist
    if not os.path.exists(updated_keywords_path):
        print(f"Error: Updated keywords file not found at {updated_keywords_path}")
        return False
    
    if not os.path.exists(ml_analyzer_path):
        print(f"Error: ML analyzer file not found at {ml_analyzer_path}")
        return False
    
    # Create a backup of the original file
    backup_path = ml_analyzer_path + '.bak'
    shutil.copy2(ml_analyzer_path, backup_path)
    print(f"Created backup of original file at {backup_path}")
    
    # Read the updated keywords
    with open(updated_keywords_path, 'r') as f:
        updated_keywords_content = f.read()
    
    # Extract the IPC_KEYWORDS dictionary
    keywords_match = re.search(r'IPC_KEYWORDS\s*=\s*\{.*?\}', updated_keywords_content, re.DOTALL)
    if not keywords_match:
        print("Error: Could not find IPC_KEYWORDS dictionary in the updated file")
        return False
    
    updated_dict = keywords_match.group(0)
    
    # Read the ML analyzer file
    with open(ml_analyzer_path, 'r') as f:
        ml_analyzer_content = f.read()
    
    # Find the IPC_KEYWORDS dictionary in the file
    start_pattern = "IPC_KEYWORDS = {"
    start_idx = ml_analyzer_content.find(start_pattern)
    if start_idx == -1:
        print("Error: Could not find IPC_KEYWORDS dictionary in the ML analyzer file")
        return False
    
    # Find the matching closing brace
    brace_count = 1
    end_idx = start_idx + len(start_pattern)
    while brace_count > 0 and end_idx < len(ml_analyzer_content):
        if ml_analyzer_content[end_idx] == '{':
            brace_count += 1
        elif ml_analyzer_content[end_idx] == '}':
            brace_count -= 1
        end_idx += 1
    
    if brace_count != 0:
        print("Error: Could not find the end of IPC_KEYWORDS dictionary")
        return False
    
    # Replace the dictionary in the file
    new_content = ml_analyzer_content[:start_idx] + updated_dict + ml_analyzer_content[end_idx:]
    
    # Write the updated file
    with open(ml_analyzer_path, 'w') as f:
        f.write(new_content)
    
    print(f"Successfully updated {ml_analyzer_path} with the new IPC_KEYWORDS dictionary")
    print("The model now includes all IPC sections from the database")
    print("\nPlease restart the application for the changes to take effect")
    
    return True

if __name__ == "__main__":
    apply_updates()
