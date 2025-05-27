"""
Test script for the chatbot functionality.
"""

import requests
import json
import sys

# Constants
API_URL = "http://localhost:5000/chatbot/api/query"

def test_chatbot_query(query):
    """
    Test the chatbot with a specific query.
    
    Args:
        query: The query to send to the chatbot
        
    Returns:
        The chatbot's response
    """
    try:
        print(f"Sending query to chatbot: '{query}'")
        
        # Send the query to the chatbot API
        response = requests.post(
            API_URL,
            json={"query": query},
            headers={"Content-Type": "application/json"}
        )
        
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the response
            data = response.json()
            
            # Print the response
            print("\nChatbot response:")
            print("-" * 80)
            print(data.get("text", "No response text"))
            print("-" * 80)
            
            # Return the response data
            return data
        else:
            print(f"Error: Received status code {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def main():
    """Main function to run the test script."""
    # Check if a query was provided as a command-line argument
    if len(sys.argv) > 1:
        # Join all arguments to form the query
        query = " ".join(sys.argv[1:])
    else:
        # Use a default query
        query = "Someone stole my phone yesterday"
    
    # Test the chatbot with the query
    test_chatbot_query(query)

if __name__ == "__main__":
    main()
