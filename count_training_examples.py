"""
Script to count the number of training examples in the model.
"""

import os
import re

def count_examples_in_file(file_path):
    """Count the number of training examples in a file."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            
            # Count the number of tuples in the file
            # This pattern matches tuples like ("text", ["code"])
            pattern = r'\(\s*"[^"]*"\s*,\s*\[[^\]]*\]\s*\)'
            matches = re.findall(pattern, content)
            
            return len(matches)
    except Exception as e:
        print(f"Error reading file {file_path}: {str(e)}")
        return 0

def count_examples_in_ml_analyzer():
    """Count the number of training examples in the ml_analyzer.py file."""
    try:
        with open('utils/ml_analyzer.py', 'r') as f:
            content = f.read()
            
            # Find the training_data list
            training_data_match = re.search(r'training_data\s*=\s*\[(.*?)\]', content, re.DOTALL)
            if not training_data_match:
                return 0
                
            training_data_content = training_data_match.group(1)
            
            # Count the number of tuples in the training data
            pattern = r'\(\s*"[^"]*"\s*,\s*\[[^\]]*\]\s*\)'
            matches = re.findall(pattern, training_data_content)
            
            return len(matches)
    except Exception as e:
        print(f"Error reading ml_analyzer.py: {str(e)}")
        return 0

def main():
    """Count the total number of training examples."""
    # Count examples in training_data.py if it exists
    training_data_count = 0
    if os.path.exists('utils/training_data.py'):
        training_data_count = count_examples_in_file('utils/training_data.py')
        print(f"Training examples in training_data.py: {training_data_count}")
    
    # Count examples in ml_analyzer.py
    ml_analyzer_count = count_examples_in_ml_analyzer()
    print(f"Training examples in ml_analyzer.py: {ml_analyzer_count}")
    
    # Total count
    total_count = training_data_count + ml_analyzer_count
    print(f"Total training examples: {total_count}")
    
    # Count unique IPC sections
    sections = set()
    
    # Extract sections from training_data.py
    if os.path.exists('utils/training_data.py'):
        with open('utils/training_data.py', 'r') as f:
            content = f.read()
            section_matches = re.findall(r'\[\s*\'([^\']+)\'\s*\]', content)
            for match in section_matches:
                sections.add(match)
    
    # Extract sections from ml_analyzer.py
    with open('utils/ml_analyzer.py', 'r') as f:
        content = f.read()
        training_data_match = re.search(r'training_data\s*=\s*\[(.*?)\]', content, re.DOTALL)
        if training_data_match:
            training_data_content = training_data_match.group(1)
            section_matches = re.findall(r'\[\s*"([^"]+)"\s*\]', training_data_content)
            for match in section_matches:
                sections.add(match)
    
    print(f"Number of unique IPC sections in training data: {len(sections)}")
    print(f"IPC sections: {', '.join(sorted(sections))}")

if __name__ == "__main__":
    main()
