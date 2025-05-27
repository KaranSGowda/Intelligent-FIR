"""
Test the chatbot route directly with misspelled queries.
"""

import os
import sys
import json
import requests

# Set the base URL for the API
BASE_URL = "http://localhost:5000"

def test_chatbot_query(query):
    """Test the chatbot with a specific query."""
    print(f"Testing chatbot with query: '{query}'")

    # Send the query to the chatbot API
    response = requests.post(
        f"{BASE_URL}/chatbot/api/query",
        json={"query": query}
    )

    # Check if the request was successful
    if response.status_code == 200:
        result = response.json()
        print("\nChatbot response:")
        print("-" * 80)
        print(result.get('text', 'No response text'))
        print("-" * 80)

        # Check if there's analysis data
        if 'data' in result and 'analysis' in result['data'] and 'sections' in result['data']['analysis']:
            sections = result['data']['analysis']['sections']
            print(f"\nFound {len(sections)} sections:")
            for section in sections:
                confidence = section.get('confidence', 0)
                print(f"- Section {section['section_code']}: {section['section_name']} (Confidence: {confidence:.2%})")
                if 'relevance' in section:
                    print(f"  Relevance: {section['relevance']}")
                if 'keywords_matched' in section:
                    print(f"  Keywords matched: {', '.join(section['keywords_matched'])}")
                print()
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    # Test with various misspelled queries
    test_cases = [
        "i mudered a person",
        "someone was murderd yesterday",
        "he stabed me with a knife",
        "i was robed at gunpoint",
        "the theif stole my wallet",
        "i was asaulted by my neighbor",
        "someone is harrasing me online",
        "i was cheeted by a seller",
        "my child was kidnaped",
        "i was defamed on social media"
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n=== Test Case {i}/{len(test_cases)} ===")
        test_chatbot_query(test_case)
        print("=" * 80)
