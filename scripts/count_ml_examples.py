"""
Script to count the number of training examples in the ML analyzer.
"""

def count_examples():
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

        print(f"Found {section_count} section comments")
        return example_count
    except Exception as e:
        print(f"Error reading ml_analyzer.py: {str(e)}")
        return 0

if __name__ == "__main__":
    count = count_examples()
    print(f"Training examples in ml_analyzer.py: {count}")
