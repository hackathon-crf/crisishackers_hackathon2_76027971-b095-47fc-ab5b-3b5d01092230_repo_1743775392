from fastapi import FastAPI, APIRouter, Body
from fastapi.middleware.cors import CORSMiddleware
from backend.app.services import (
    test_service, get_mistral_response, 
    generate_crisis_scenario, process_user_decision, 
    generate_crisis_advice
)
from settings.config import settings
from typing import List, Dict, Any, Optional


app_router = APIRouter(
    prefix="/api/app",
    tags=["Retrieval QA"],
)

def create_app(root_path: str = "") -> FastAPI:
    """
    Creating a FastAPI instance and registering routes.

    Args:
        root_path: The root path where the API is mounted (e.g., /username/app_name)
    """

    backend_app = FastAPI(
        title="Template App",
        version="1.0.0",
        openapi_version="3.1.0",
        root_path=root_path
    )

    # CORS Configuration
    backend_app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_HOSTS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    # Registering routes
    backend_app.include_router(app_router)
    return backend_app

@app_router.get("/test/")
async def test():
        return {
            "status:": 200,
            "message": test_service(),
            "data": {
                "title": "here is some example data",
                "genAI_info": {
                    "use_cases": ["Chatbot creation", "Content generation", "Data augmentation",
                                  "Customer support automation"],
                    "key_features": {
                        "personalization": "Generates tailored responses based on user input and context.",
                        "RAG_integration": "Utilizes external knowledge sources to enhance generated responses.",
                        "no_code": "Allows non-technical users to build AI-powered chatbots easily.",
                        "security": "Ensures data privacy with secure integrations and compliance."
                    },
                    "user_examples": [
                        {"name": "John", "use_case": "E-commerce chatbot", "result": "Improved customer engagement by 25%"},
                        {"name": "Sara", "use_case": "Content creation",
                         "result": "Saved 10 hours weekly on content production"}
                    ]
                },
                "additional_metrics": {
                    "response_time_ms": 150,
                    "api_version": "1.0.2"
                }
            }
        }

@app_router.post("/chat/")
async def chat(conversation: List[Dict[str, str]] = Body(...)):
    """
    Process chat messages and get response from Mistral API.
    
    Args:
        conversation: List of message dictionaries with 'role' and 'content'
    
    Returns:
        Response from Mistral API or error message
    """
    try:
        response = get_mistral_response(conversation)
        if response:
            return {
                "status": 200,
                "message": "Chat response generated successfully",
                "data": {
                    "response": response
                }
            }
        else:
            return {
                "status": 500,
                "message": "Failed to get response from Mistral API",
                "data": None
            }
    except Exception as e:
        return {
            "status": 500,
            "message": f"An error occurred: {str(e)}",
            "data": None
        }

@app_router.post("/crisis/scenario")
async def create_crisis_scenario(initial_state: Dict[str, Any] = Body(...)):
    """
    Generate a crisis scenario based on the user's profile and initial state.
    
    Args:
        initial_state: Dictionary containing the user's profile and starting state
    
    Returns:
        Generated scenario description or error message
    """
    try:
        scenario = generate_crisis_scenario(initial_state)
        if scenario:
            return {
                "status": 200,
                "message": "Crisis scenario generated successfully",
                "data": {
                    "scenario": scenario
                }
            }
        else:
            return {
                "status": 500,
                "message": "Failed to generate crisis scenario",
                "data": None
            }
    except Exception as e:
        return {
            "status": 500,
            "message": f"An error occurred: {str(e)}",
            "data": None
        }

@app_router.post("/crisis/decision")
async def process_decision(
    request: Dict[str, Any] = Body(...)
):
    """
    Process a user's decision in the crisis simulation.
    
    Args:
        request: Dictionary containing state, user_action, and recent_events
    
    Returns:
        Next situation description and JSON modifications or error message
    """
    try:
        state = request.get("state", {})
        user_action = request.get("user_action", "")
        recent_events = request.get("recent_events", [])
        
        result = process_user_decision(state, user_action, recent_events)
        
        if result:
            next_situation, json_modifications = result
            return {
                "status": 200,
                "message": "Decision processed successfully",
                "data": {
                    "next_situation": next_situation,
                    "json_modifications": json_modifications
                }
            }
        else:
            return {
                "status": 500,
                "message": "Failed to process decision",
                "data": None
            }
    except Exception as e:
        return {
            "status": 500,
            "message": f"An error occurred: {str(e)}",
            "data": None
        }

@app_router.post("/crisis/advice")
async def get_crisis_advice(
    request: Dict[str, Any] = Body(...)
):
    """
    Generate personalized advice based on the crisis simulation results.
    
    Args:
        request: Dictionary containing profile, final_state, and simulation_log
    
    Returns:
        Personalized advice or error message
    """
    try:
        profile = request.get("profile", {})
        final_state = request.get("final_state", {})
        simulation_log = request.get("simulation_log", [])
        
        advice = generate_crisis_advice(profile, final_state, simulation_log)
        
        if advice:
            return {
                "status": 200,
                "message": "Advice generated successfully",
                "data": {
                    "advice": advice
                }
            }
        else:
            return {
                "status": 500,
                "message": "Failed to generate advice",
                "data": None
            }
    except Exception as e:
        return {
            "status": 500,
            "message": f"An error occurred: {str(e)}",
            "data": None
        }