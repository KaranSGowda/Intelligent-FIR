"""
Test script to evaluate the accuracy of the IPC section prediction model.
"""

import sys
import os
import json
from collections import defaultdict

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import Flask app and the analyze_complaint function
from app import app
from utils.ml_analyzer import analyze_complaint

# Test cases with expected IPC sections
TEST_CASES = [
    # Theft cases
    {
        "description": "Someone stole my mobile phone from my pocket in the market",
        "expected_sections": ["379"]
    },
    {
        "description": "My house was broken into and my laptop and jewelry were stolen",
        "expected_sections": ["380"]
    },
    {
        "description": "My servant stole money from my wallet",
        "expected_sections": ["381"]
    },

    # Assault cases
    {
        "description": "I was assaulted by my neighbor who hit me with his fists",
        "expected_sections": ["323"]
    },
    {
        "description": "Someone attacked me with a knife and injured my arm",
        "expected_sections": ["324"]
    },
    {
        "description": "I was severely beaten by a group of people causing fractures",
        "expected_sections": ["325"]
    },

    # Murder/Homicide cases
    {
        "description": "I witnessed a person being stabbed to death in the park",
        "expected_sections": ["302"]
    },
    {
        "description": "A person died due to reckless driving by a truck driver",
        "expected_sections": ["304A"]
    },
    {
        "description": "Someone tried to kill me by poisoning my food but I survived after hospital treatment",
        "expected_sections": ["307"]
    },

    # Sexual offenses
    {
        "description": "A man inappropriately touched a woman in the bus without her consent",
        "expected_sections": ["354"]
    },
    {
        "description": "A woman was sexually assaulted by her colleague",
        "expected_sections": ["376"]
    },

    # Fraud/Cheating cases
    {
        "description": "I was cheated by an online seller who took my money but never delivered the product",
        "expected_sections": ["420"]
    },
    {
        "description": "A person misappropriated funds that were entrusted to him for investment",
        "expected_sections": ["406"]
    },

    # Domestic violence
    {
        "description": "A woman is being harassed by her husband and in-laws for dowry",
        "expected_sections": ["498A"]
    },

    # Criminal intimidation
    {
        "description": "My neighbor threatened to kill me if I don't withdraw my complaint",
        "expected_sections": ["506"]
    },

    # False cases (non-crimes or figurative language)
    {
        "description": "The beauty of the sunset was absolutely killing me",
        "expected_sections": []  # Should not match any IPC section
    },
    {
        "description": "I watched a movie about a theft yesterday",
        "expected_sections": []  # Should not match any IPC section
    },
    {
        "description": "I had a great day at the park yesterday",
        "expected_sections": []  # Should not match any IPC section
    }
]

def evaluate_model():
    """Evaluate the model's accuracy on the test cases."""
    print("Evaluating IPC section prediction model accuracy...\n")

    total_cases = len(TEST_CASES)
    correct_predictions = 0
    false_positives = 0
    false_negatives = 0

    # Detailed results for each case
    results = []

    # Confusion matrix for each section
    section_metrics = defaultdict(lambda: {"tp": 0, "fp": 0, "fn": 0})

    for i, test_case in enumerate(TEST_CASES, 1):
        description = test_case["description"]
        expected_sections = test_case["expected_sections"]

        print(f"Test Case {i}/{total_cases}: {description[:50]}...")

        # Get model predictions
        analysis_result = analyze_complaint(description)
        predicted_sections = [section["section_code"] for section in analysis_result.get("sections", [])]

        # Filter out low confidence predictions (below 20%)
        predicted_sections = [
            section["section_code"]
            for section in analysis_result.get("sections", [])
            if section.get("confidence", 0) >= 0.2
        ]

        # Check if prediction is correct
        is_correct = False

        if not expected_sections and not predicted_sections:
            # True negative - correctly identified non-crime
            is_correct = True
        elif expected_sections:
            # Check if at least one expected section is in the predicted sections
            if any(section in predicted_sections for section in expected_sections):
                is_correct = True

        # Update metrics
        if is_correct:
            correct_predictions += 1

        # Track false positives and false negatives for each section
        all_sections = set(expected_sections + predicted_sections)
        for section in all_sections:
            is_expected = section in expected_sections
            is_predicted = section in predicted_sections

            if is_expected and is_predicted:
                # True positive
                section_metrics[section]["tp"] += 1
            elif not is_expected and is_predicted:
                # False positive
                section_metrics[section]["fp"] += 1
                false_positives += 1
            elif is_expected and not is_predicted:
                # False negative
                section_metrics[section]["fn"] += 1
                false_negatives += 1

        # Store detailed result
        results.append({
            "description": description,
            "expected_sections": expected_sections,
            "predicted_sections": predicted_sections,
            "is_correct": is_correct
        })

        # Print result
        print(f"  Expected: {expected_sections}")
        print(f"  Predicted: {predicted_sections}")
        print(f"  Result: {'✓ CORRECT' if is_correct else '✗ INCORRECT'}\n")

    # Calculate overall accuracy
    accuracy = correct_predictions / total_cases if total_cases > 0 else 0

    # Calculate precision and recall for each section
    section_performance = {}
    for section, metrics in section_metrics.items():
        tp = metrics["tp"]
        fp = metrics["fp"]
        fn = metrics["fn"]

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

        section_performance[section] = {
            "precision": precision,
            "recall": recall,
            "f1_score": f1_score
        }

    # Print summary
    print("\n=== MODEL ACCURACY SUMMARY ===")
    print(f"Total test cases: {total_cases}")
    print(f"Correct predictions: {correct_predictions}")
    print(f"False positives: {false_positives}")
    print(f"False negatives: {false_negatives}")
    print(f"Overall accuracy: {accuracy:.2%}")

    # Print section-specific metrics
    print("\n=== SECTION-SPECIFIC METRICS ===")
    for section, metrics in sorted(section_performance.items()):
        print(f"Section {section}:")
        print(f"  Precision: {metrics['precision']:.2%}")
        print(f"  Recall: {metrics['recall']:.2%}")
        print(f"  F1 Score: {metrics['f1_score']:.2%}")

    return {
        "accuracy": accuracy,
        "correct_predictions": correct_predictions,
        "total_cases": total_cases,
        "false_positives": false_positives,
        "false_negatives": false_negatives,
        "section_performance": section_performance,
        "detailed_results": results
    }

if __name__ == "__main__":
    # Run within Flask application context
    with app.app_context():
        evaluate_model()
