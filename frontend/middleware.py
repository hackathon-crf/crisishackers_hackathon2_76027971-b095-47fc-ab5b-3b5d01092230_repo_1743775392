import requests
from settings.config import settings
from dotenv import load_dotenv
import os
import logging
from typing import List, Dict, Optional, Any

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/middleware.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("frontend.middleware")

# Load environment variables from .client_env
load_dotenv(".client_env")

# Get environment variables, with fallbacks
DOMAIN_NAME = os.getenv("DOMAIN_NAME", "localhost")
ROOT_PATH = os.getenv("ROOT_PATH", "")
BACKEND_PORT = os.getenv("BACKEND_PORT", "8090")

def get_backend_base_url():
    """Get base URL for backend API calls"""
    # Handle both localhost and remote deployments
    if DOMAIN_NAME == "localhost":
        # For local development, use HTTP and include port
        return f"http://{DOMAIN_NAME}:{BACKEND_PORT}{ROOT_PATH}"
    else:
        # For deployed environment, use HTTPS without port
        return f"https://{DOMAIN_NAME}{ROOT_PATH}"

def call_backend_test():
    try:
        # Construct URL with proper protocol and format
        base_url = get_backend_base_url()
        url = f"{base_url}/api/app/test/"
        logger.debug(f"Calling backend URL: {url}")

        params = {}
        response = requests.get(url, params=params)
        logger.debug(f"Response status: {response.status_code}")
        return response.json()
    except Exception as e:
        logger.error(f"Error calling backend: {str(e)}")
        return {"error": str(e)}

def call_chat_endpoint(conversation_history: List[Dict[str, str]]) -> Optional[Dict[str, Any]]:
    """
    Call the backend chat endpoint with the provided conversation history.
    
    Args:
        conversation_history: List of message dictionaries with 'role' and 'content'
        
    Returns:
        Response JSON from the backend or None if the request fails
    """
    try:
        # Construct URL
        base_url = get_backend_base_url()
        url = f"{base_url}/api/app/chat/"
        logger.debug(f"Calling chat endpoint: {url}")
        
        # Make request
        response = requests.post(url, json=conversation_history)
        logger.debug(f"Response status: {response.status_code}")
        
        # Return response JSON
        return response.json()
    except Exception as e:
        logger.error(f"Error calling chat endpoint: {str(e)}")
        return None

def call_crisis_scenario(initial_state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Call the backend crisis scenario generation endpoint.
    
    Args:
        initial_state: Dictionary containing the user's profile and starting state
        
    Returns:
        Response JSON from the backend or None if the request fails
    """
    try:
        # Construct URL
        base_url = get_backend_base_url()
        url = f"{base_url}/api/app/crisis/scenario"
        logger.debug(f"Calling crisis scenario endpoint: {url}")
        
        # Make request
        response = requests.post(url, json=initial_state)
        logger.debug(f"Response status: {response.status_code}")
        
        # Return response JSON
        return response.json()
    except Exception as e:
        logger.error(f"Error calling crisis scenario endpoint: {str(e)}")
        return None

def call_crisis_decision(request_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Call the backend decision processing endpoint.
    
    Args:
        request_data: Dictionary containing state, user_action, and recent_events
        
    Returns:
        Response JSON from the backend or None if the request fails
    """
    try:
        # Construct URL
        base_url = get_backend_base_url()
        url = f"{base_url}/api/app/crisis/decision"
        logger.debug(f"Calling crisis decision endpoint: {url}")
        
        # Make request
        response = requests.post(url, json=request_data)
        logger.debug(f"Response status: {response.status_code}")
        
        # Return response JSON
        return response.json()
    except Exception as e:
        logger.error(f"Error calling crisis decision endpoint: {str(e)}")
        return None

def call_crisis_advice(request_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Call the backend advice generation endpoint.
    
    Args:
        request_data: Dictionary containing profile, final_state, and simulation_log
        
    Returns:
        Response JSON from the backend or None if the request fails
    """
    try:
        # Construct URL
        base_url = get_backend_base_url()
        url = f"{base_url}/api/app/crisis/advice"
        logger.debug(f"Calling crisis advice endpoint: {url}")
        
        # Make request
        response = requests.post(url, json=request_data)
        logger.debug(f"Response status: {response.status_code}")
        
        # Return response JSON
        return response.json()
    except Exception as e:
        logger.error(f"Error calling crisis advice endpoint: {str(e)}")
        return None