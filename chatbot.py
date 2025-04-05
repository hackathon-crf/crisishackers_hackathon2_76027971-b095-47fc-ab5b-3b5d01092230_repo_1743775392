#!/usr/bin/env python3
"""
Simple command-line chatbot using the Mistral API
"""

import os
import requests
import argparse
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable
API_KEY = os.environ.get("MISTRAL_API_KEY")
if not API_KEY:
    print("Error: MISTRAL_API_KEY environment variable not set")
    print("Please set it using 'export MISTRAL_API_KEY=your_api_key' or create a .env file")
    exit(1)

def get_mistral_response(conversation_history, model="mistral-large-latest"):
    """
    Call Mistral API with the given conversation history
    
    Args:
        conversation_history: List of message dictionaries with 'role' and 'content'
        model: Mistral model to use
        
    Returns:
        Assistant's response or None if the API call fails
    """
    # API endpoint
    endpoint = "https://api.mistral.ai/v1/chat/completions"
    
    # Headers
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    # Request payload
    payload = {
        "model": model,
        "messages": conversation_history,
        "temperature": 0.7,
        "max_tokens": 1000
    }
    
    try:
        # Make the API request
        response = requests.post(endpoint, headers=headers, json=payload)
        response.raise_for_status()
        
        # Parse the response
        result = response.json()
        
        # Extract and return the assistant's message
        return result.get("choices", [{}])[0].get("message", {}).get("content", "")
    
    except requests.RequestException as e:
        print(f"API request error: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Status code: {e.response.status_code}")
            print(f"Response content: {e.response.text}")
        return None

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Simple Mistral AI Chatbot")
    parser.add_argument("--model", type=str, default="mistral-large-latest", 
                        help="Mistral model to use (default: mistral-large-latest)")
    parser.add_argument("--max-history", type=int, default=10,
                        help="Maximum number of message pairs to keep in history (default: 10)")
    args = parser.parse_args()
    
    # Initialize conversation history
    conversation_history = []
    
    # Welcome message
    print("Welcome to the Mistral AI Chatbot!")
    print("Type 'exit' or 'quit' to end the conversation.")
    print("Type 'clear' to clear the conversation history.")
    print()
    
    # Main interaction loop
    while True:
        # Get user input
        user_input = input("You: ")
        
        # Check for exit command
        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break
        
        # Check for clear command
        if user_input.lower() == "clear":
            conversation_history = []
            print("Conversation history cleared.")
            continue
        
        # Add user message to history
        conversation_history.append({"role": "user", "content": user_input})
        
        # Trim history if needed
        if args.max_history > 0 and len(conversation_history) > args.max_history * 2:
            # Keep the first message (system prompt) if it exists and has role 'system'
            if conversation_history and conversation_history[0].get("role") == "system":
                conversation_history = [conversation_history[0]] + conversation_history[-args.max_history*2 + 1:]
            else:
                conversation_history = conversation_history[-args.max_history*2:]
        
        # Get response from Mistral
        print("Chatbot is thinking...")
        response = get_mistral_response(conversation_history, model=args.model)
        
        if response:
            # Print the response
            print(f"Chatbot: {response}")
            
            # Add assistant message to history
            conversation_history.append({"role": "assistant", "content": response})
        else:
            print("Error: Failed to get response from Mistral API")

if __name__ == "__main__":
    main()