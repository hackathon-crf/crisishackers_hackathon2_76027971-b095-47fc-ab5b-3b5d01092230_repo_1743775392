#!/usr/bin/env python3
"""
Test script to verify Mistral API connectivity and make a sample request.
"""

import os
import json
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def test_mistral_api():
    """
    Test connection to Mistral API by sending a simple request
    """
    print("Testing Mistral API connectivity...")
    
    # Get API key from environment variable
    API_KEY = os.environ.get("MISTRAL_API_KEY")
    if not API_KEY:
        print("\n❌ ERROR: MISTRAL_API_KEY environment variable not set")
        print("Please set it using 'export MISTRAL_API_KEY=your_api_key' or create a .env file")
        return False
    
    print(f"✓ Found API key (first 4 chars: {API_KEY[:4]}...)")
    
    # API endpoint
    endpoint = "https://api.mistral.ai/v1/chat/completions"
    
    # Headers
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    # Simple test message
    messages = [
        {"role": "user", "content": "Hello, can you give me a brief response to test connectivity?"}
    ]
    
    # Request payload
    payload = {
        "model": "mistral-small-latest",  # Use the smallest model for testing
        "messages": messages,
        "max_tokens": 50,
        "temperature": 0.5
    }
    
    try:
        print("Sending test request to Mistral API...")
        response = requests.post(endpoint, headers=headers, json=payload)
        
        # Check status code
        if response.status_code == 200:
            result = response.json()
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            print(f"\n✅ SUCCESS! Status code: {response.status_code}")
            print("\nResponse preview:")
            print(f"  {content[:100]}...")
            
            print("\nResponse headers:")
            for key, value in response.headers.items():
                if key.lower() in ["content-type", "x-ratelimit-remaining", "x-ratelimit-limit"]:
                    print(f"  {key}: {value}")
            
            return True
        else:
            print(f"\n❌ ERROR: Status code {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_mistral_api()
    if success:
        print("\n🎉 Mistral API is working correctly!")
    else:
        print("\n❌ Mistral API test failed. Please check your API key and network connection.")