"""
Script to count all training examples in the model.
"""

def count_ml_analyzer_examples():
    """Count the number of training examples in the ML analyzer."""
    try:
        # Count the number of lines that start with a comment indicating a section
        section_count = 0
        example_count = 0
        
        with open('utils/ml_analyzer.py', 'r') as f:
            in_training_data = False
            for line in f:
                line = line.strip()
                
                # Check if we're in the training data section
                if line == "training_data = [":
                    in_training_data = True
                    continue
                elif line == "]" and in_training_data:
                    in_training_data = False
                    continue
                
                # Count examples in the training data section
                if in_training_data:
                    if line.startswith("# Section"):
                        section_count += 1
                    elif line.startswith("(\"") and "])" in line:
                        example_count += 1
        
        print(f"Found {section_count} section comments in ml_analyzer.py")
        return example_count
    except Exception as e:
        print(f"Error reading ml_analyzer.py: {str(e)}")
        return 0

def count_training_data_examples():
    """Count the number of training examples in training_data.py."""
    try:
        example_count = 0
        
        with open('utils/training_data.py', 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith("(\"") or line.startswith("('"):
                    example_count += 1
        
        return example_count
    except Exception as e:
        print(f"Error reading training_data.py: {str(e)}")
        return 0

def main():
    """Count all training examples."""
    ml_analyzer_count = count_ml_analyzer_examples()
    print(f"Training examples in ml_analyzer.py: {ml_analyzer_count}")
    
    training_data_count = count_training_data_examples()
    print(f"Training examples in training_data.py: {training_data_count}")
    
    total_count = ml_analyzer_count + training_data_count
    print(f"Total training examples: {total_count}")

if __name__ == "__main__":
    main()
