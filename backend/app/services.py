import os
import requests
import json
import re
from typing import List, Dict, Any, Optional, Tuple
from dotenv import load_dotenv
from backend.app.back_utils import load_api_key
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/services.log"),
        logging.StreamHandler()
    ]
)

RAG_API_ENDPOINT="https://hackathon-ia-et-crise.fr/admin/rag-system/api/app"
MISTRAL_API_KEY ="pJKvqp2uKF9PkULrp6LywyBsDHWaWnQZ"

logger = logging.getLogger("backend.services")

# Load environment variables
load_dotenv()

def test_service():
    return "Backend connected successfully!"

def get_mistral_response(conversation_history: List[Dict[str, str]], 
                         model: str = "mistral-large-latest", 
                         temperature: float = 0.7,
                         max_tokens: int = 1000) -> Optional[str]:
    """
    Call Mistral API with the given conversation history.
    
    Args:
        conversation_history: List of message dictionaries with 'role' and 'content'
        model: Mistral model to use
        temperature: Sampling temperature (0.0-1.0)
        max_tokens: Maximum tokens to generate
        
    Returns:
        Assistant's response or None if the API call fails
    """
    try:
        # Get API key
        api_key = load_api_key()
        
        # API endpoint
        endpoint = "https://api.mistral.ai/v1/chat/completions"
        
        # Headers
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        # Request payload
        payload = {
            "model": model,
            "messages": conversation_history,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        logger.debug(f"Calling Mistral API with model: {model}, max_tokens: {max_tokens}")
        
        # Make the API request
        response = requests.post(endpoint, headers=headers, json=payload)
        response.raise_for_status()  # Raise exception for error status codes
        
        # Parse the response
        result = response.json()
        
        # Extract and return the assistant's message
        content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
        logger.debug(f"Got response from Mistral API: {len(content)} characters")
        return content
    
    except requests.RequestException as e:
        logger.error(f"API request error: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Status code: {e.response.status_code}")
            logger.error(f"Response content: {e.response.text}")
        return None
    except Exception as e:
        logger.error(f"Error in get_mistral_response: {str(e)}")
        return None

def get_embeddings(query, collection_name):
    """
    Get embeddings for a query using the specified collection.

    Args:
        query (str): The query text to get embeddings for
        collection_name (str): The name of the collection to use

    Returns:
        The embeddings response
    """
    print_step(2, "Getting Embeddings for Query")
    try:
        # Construct the URL
        url = f"{RAG_API_ENDPOINT}/inferencing/get_embeddings"

        # Ensure collection is properly formatted
        if isinstance(collection_name, list):
            collection_name = collection_name[0] if collection_name else ""

        # Clean up the collection name
        collection_name = str(collection_name).strip().strip('"\'[]')

        # Set up the parameters
        params = {
            "query": query,
            "collection_name": collection_name,
            "api_key": MISTRAL_API_KEY
        }

        print(f"Calling: {url}")
        print("Parameters:")
        print_json({k: v if k != "api_key" else "****" for k, v in params.items()})

        # Make the request
        response = requests.post(url, params=params)

        print(f"Status Code: {response.status_code}")

        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            print(f"Response: {response.text}")
            return None

        # Try to parse as JSON
        try:
            result = response.json()
            print("\nEmbeddings Response:")

            # Check if the result is a string containing a large embedding vector
            if isinstance(result, str) and len(result) > 1000:
                # If it's a very long string (likely an embedding vector), just show a preview
                print(f"Received embedding vector (showing first 100 chars): {result[:100]}...")
                print(f"Full vector length: {len(result)} characters")
            else:
                print_json(result)

            return result
        except json.JSONDecodeError:
            # If it's not JSON, just return the text
            print("\nResponse (text):")
            print(response.text[:500] + "..." if len(response.text) > 500 else response.text)
            return response.text

    except Exception as e:
        print(f"Error getting embeddings: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return None

def generate_crisis_scenario(initial_state: Dict[str, Any]) -> Optional[str]:
    """
    Generate a crisis scenario based on the user's profile and initial state.
    
    Args:
        initial_state: Dictionary containing the user's profile and starting state
        
    Returns:
        Generated scenario description or None if the API call fails
    """
    logger.debug("Generating crisis scenario")
    
    query = "extrait la sitatuation de crise la plus proche du contexte suivant : PAYS ENVIRONNEMENT"
    #rag_extraction = get_embeddings(query, "situation_de_crise")

    prompt = f"""
    Génére une description concise d'un scénario d'une innondation en Haute-Saône impliquant Crisou.
    Crisou, est en Haute-Saône lorsque l'eau commence à monter rapidement suite à une inondation soudaine. Vous êtes seul et n'avez pas d'expérience particulière pour ce genre de situation. Les accès routiers autour de vous risquent d'être rapidement coupés. Quelle est votre première action pour assurer votre sécurité ?

    This JSON data representing a user's profile and starting state:
    {json.dumps(initial_state, indent=2)}
    rag_extraction
    


    """
    
    conversation = [{"role": "user", "content": prompt}]
    return get_mistral_response(conversation)

def process_user_decision(state: Dict[str, Any], user_action: str, recent_events: List[str]) -> Optional[Tuple[str, List[str]]]:
    """
    Process a user's decision in the crisis simulation.
    
    Args:
        state: Current state of the simulation
        user_action: Text of the user's action/decision
        recent_events: Recent events from the simulation log
        
    Returns:
        Tuple containing the next situation description and a list of JSON modifications,
        or None if the API call fails
    """
    logger.debug(f"Processing user decision: {user_action[:50]}...")
    
    recent_events_text = "\n".join(recent_events)
    
    prompt = f"""
    Current Simulation State (JSON):
    {json.dumps(state, indent=2)}
    
    User's Action for this Turn: "{user_action}"
    
    Recent Events:
    {recent_events_text}
    
    Based on the user's action and the current state:
    1. Describe the immediate outcome and the situation at the start of the next turn. Keep it concise.
    2. Suggest specific, incremental modifications to the JSON state reflecting these outcomes (e.g., "decrease resources.food by 1", "update family member status 'John' to 'injured'", "increment status.day by 1"). List these modifications clearly.
    
    Output format:
    NEXT_SITUATION_DESCRIPTION: [Your description here]
    JSON_MODIFICATIONS:
    - [modification 1]
    - [modification 2]
    ...
    """
    
    conversation = [{"role": "user", "content": prompt}]
    response = get_mistral_response(conversation)
    
    if not response:
        logger.error("Failed to get response for user decision")
        return None
    
    logger.debug(f"Parsing response: {len(response)} characters")
    
    # Parse the response
    next_situation_match = re.search(r"NEXT_SITUATION_DESCRIPTION:\s*(.*?)(?=\nJSON_MODIFICATIONS:|$)", response, re.DOTALL)
    next_situation = next_situation_match.group(1).strip() if next_situation_match else ""
    
    json_mods_match = re.search(r"JSON_MODIFICATIONS:\s*(.*?)(?=$)", response, re.DOTALL)
    json_mods_text = json_mods_match.group(1).strip() if json_mods_match else ""
    
    # Split the modifications into a list
    json_modifications = []
    if json_mods_text:
        # Extract items that start with a dash
        modifications = re.findall(r"- (.*?)(?=\n- |\n\n|$)", json_mods_text, re.DOTALL)
        json_modifications = [mod.strip() for mod in modifications if mod.strip()]
    
    logger.debug(f"Extracted situation ({len(next_situation)} chars) and modifications ({len(json_modifications)} items)")
    return next_situation, json_modifications

def generate_crisis_advice(profile: Dict[str, Any], final_state: Dict[str, Any], simulation_log: List[str]) -> Optional[str]:
    """
    Generate personalized advice based on the crisis simulation results.
    
    Args:
        profile: User's profile
        final_state: Final state of the simulation
        simulation_log: Log of all events in the simulation
        
    Returns:
        Personalized advice or None if the API call fails
    """
    logger.debug("Generating personalized crisis advice")
    
    prompt = f"""
    This user just completed a crisis simulation with the following:
    
    Initial Profile:
    {json.dumps(profile, indent=2)}
    
    Final State:
    {json.dumps(final_state, indent=2)}
    
    Simulation Timeline:
    {json.dumps(simulation_log, indent=2)}
    
    Based on how this simulation went, provide 3-5 practical, personalized pieces of advice to help this person prepare for a real crisis like the one simulated. Focus on specific actions they can take based on their location, vulnerabilities, and how the simulation played out.
    """
    
    conversation = [{"role": "user", "content": prompt}]
    return get_mistral_response(conversation)