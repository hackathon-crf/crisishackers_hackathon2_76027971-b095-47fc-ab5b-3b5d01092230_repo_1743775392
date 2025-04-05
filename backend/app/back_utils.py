import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test():
    return "Backend works successfully"

def load_api_key():
    """Load API key from environment variable"""
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        raise ValueError("MISTRAL_API_KEY environment variable not set")
    return api_key