import streamlit as st
import json
import requests
import re
import logging
import os
import sys
import traceback
from typing import Dict, List, Any, Tuple
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/crisis_simulation.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("crisis_simulation")

def initialize_session_state():
    """Initialize the session state variables if they don't exist"""
    logger.debug("Initializing session state")
    
    if 'app_state' not in st.session_state:
        st.session_state['app_state'] = 'collecting_info'
        logger.debug("Set initial app_state to 'collecting_info'")
    else:
        logger.debug(f"Current app_state: {st.session_state['app_state']}")
    
    if 'initial_state' not in st.session_state:
        st.session_state['initial_state'] = {}
        logger.debug("Initialized empty initial_state")
    
    if 'simulation_log' not in st.session_state:
        st.session_state['simulation_log'] = []
        logger.debug("Initialized empty simulation_log")
    
    if 'current_day' not in st.session_state:
        st.session_state['current_day'] = 0
        logger.debug("Set current_day to 0")
    
    if 'crisis_description' not in st.session_state:
        st.session_state['crisis_description'] = ""
        logger.debug("Initialized empty crisis_description")
    
    if 'latest_update' not in st.session_state:
        st.session_state['latest_update'] = ""
        logger.debug("Initialized empty latest_update")
    
    if 'debug_info' not in st.session_state:
        st.session_state['debug_info'] = []
        logger.debug("Initialized empty debug_info list")

def log_debug_info(message, data=None):
    """Log debug information and store in session state for display"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    debug_entry = {"timestamp": timestamp, "message": message, "data": data}
    
    logger.debug(f"{message} - Data: {data}")
    
    if 'debug_info' in st.session_state:
        st.session_state['debug_info'].append(debug_entry)
    else:
        st.session_state['debug_info'] = [debug_entry]

def call_mistral_api(prompt: str) -> str:
    """Call the Mistral API with the given prompt"""
    log_debug_info("Preparing to call Mistral API")
    
    # First try to get API key from Streamlit secrets
    api_key = st.secrets.get("MISTRAL_API_KEY", None)
    
    if not api_key:
        # If not in secrets, try environment variable
        api_key = os.environ.get("MISTRAL_API_KEY", None)
        log_debug_info("API key source", "environment variable" if api_key else "not found")
    else:
        log_debug_info("API key source", "streamlit secrets")
    
    if not api_key:
        error_msg = "Mistral API key not found in secrets or environment variables"
        log_debug_info(error_msg)
        st.error(error_msg)
        return ""
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    data = {
        "model": "mistral-large-latest",
        "Based on this, can you generate a crisis scenario to immerse Crisou in? This crisis should be designed to best prepare the player for the most likely situation they could encounter based on their location. Your description of the crisis should remain concise but include enough detail to allow the player to make informed decisions.": prompt,
        "max_tokens": 1000,
        "temperature": 0.7,
    }
    
    log_debug_info("API request data", {"model": data["model"], "max_tokens": data["max_tokens"], "prompt_length": len(prompt)})
    
    try:
        log_debug_info("Sending request to Mistral API")
        response = requests.post(
            "https://api.mistral.ai/v1/chat/completions",
            headers=headers,
            json=data
        )
        
        log_debug_info(f"API response status code: {response.status_code}")
        
        if response.status_code != 200:
            log_debug_info("API error response", response.text)
            return ""
            
        result = response.json()
        log_debug_info("API response received", {"choices_count": len(result.get("choices", []))})
        
        content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
        log_debug_info("Extracted content", {"content_length": len(content), "content_preview": content[:50] + "..." if len(content) > 50 else content})
        
        return content
    except Exception as e:
        error_msg = f"Error calling Mistral API: {str(e)}"
        log_debug_info(error_msg)
        log_debug_info("Exception traceback", traceback.format_exc())
        st.error(error_msg)
        return ""

def render_input_form():
    """Render the form to collect user information"""
    st.title("Crisis Simulation Setup")
    st.write("Please provide information about yourself to generate a personalized crisis scenario.")
    
    with st.form("user_info_form"):
        name = st.text_input("Your Name")
        age = st.number_input("Your Age", min_value=1, max_value=120, value=30)
        location = st.text_input("Your Current Location (be specific - City/Region/Country)")
        family = st.text_area("Family Members (e.g., '2 adults, 1 child (age 5), 1 dog')")
        vulnerabilities = st.text_area("Vulnerabilities (e.g., 'Child has asthma, limited savings, live on 3rd floor apartment')")
        
        submit_button = st.form_submit_button("Start Simulation")
        
        if submit_button:
            log_debug_info("Form submitted", {
                "name": name,
                "age": age,
                "location": location,
                "family_length": len(family),
                "vulnerabilities_length": len(vulnerabilities)
            })
            
            if not (name and location):
                error_msg = "Please fill in all required fields (Name and Location)."
                log_debug_info(error_msg)
                st.error(error_msg)
                return
            
            # Store collected data in session state
            st.session_state['initial_state'] = {
                "profile": {
                    "name": name,
                    "age": age,
                    "location": location
                },
                "family": family,
                "vulnerabilities": vulnerabilities,
                "resources": {
                    "food": 10,
                    "water": 10,
                    "medicine": 5,
                    "morale": 8
                },
                "status": "Day 1"
            }
            
            log_debug_info("Updated initial_state", st.session_state['initial_state'])
            log_debug_info("Changing app_state to 'generating_scenario'")
            st.session_state['app_state'] = 'generating_scenario'
            st.rerun()

def generate_crisis_scenario():
    """Generate the initial crisis scenario using Mistral API"""
    st.title("Generating Crisis Scenario")
    log_debug_info("Entering generate_crisis_scenario")
    
    with st.spinner("Generating a personalized crisis scenario based on your location and information..."):
        log_debug_info("Preparing prompt for crisis scenario generation")
        prompt = f"""
        Based on this JSON data representing a user's profile and starting state:
        {json.dumps(st.session_state['initial_state'], indent=2)}
        
        Generate a concise crisis scenario description. This crisis should be the most likely type the user might encounter based primarily on their 'location'. The description must be detailed enough to allow the user to make an informed first decision, but remain relatively brief. Output *only* the scenario description text.
        """
        
        log_debug_info("Calling Mistral API for scenario generation")
        scenario_description = call_mistral_api(prompt)
        
        if scenario_description:
            log_debug_info("Received scenario description", {
                "description_length": len(scenario_description),
                "preview": scenario_description[:100] + "..." if len(scenario_description) > 100 else scenario_description
            })
            
            st.session_state['crisis_description'] = scenario_description
            st.session_state['latest_update'] = scenario_description
            st.session_state['simulation_log'] = [scenario_description]
            st.session_state['current_day'] = 1
            
            log_debug_info("Updated session state variables", {
                "current_day": st.session_state['current_day'],
                "simulation_log_length": len(st.session_state['simulation_log'])
            })
            
            log_debug_info("Changing app_state to 'in_simulation'")
            st.session_state['app_state'] = 'in_simulation'
            st.rerun()
        else:
            error_msg = "Failed to generate a crisis scenario. Please try again."
            log_debug_info(error_msg)
            st.error(error_msg)
            st.button("Try Again", on_click=lambda: None)

def parse_mistral_response(response: str) -> Tuple[str, List[str]]:
    """Parse the Mistral API response to extract the next situation description and JSON modifications"""
    log_debug_info("Parsing Mistral response", {"response_length": len(response)})
    
    # Extract the next situation description
    next_situation_match = re.search(r"NEXT_SITUATION_DESCRIPTION:\s*(.*?)(?=\nJSON_MODIFICATIONS:|$)", response, re.DOTALL)
    next_situation = next_situation_match.group(1).strip() if next_situation_match else ""
    
    log_debug_info("Extracted next situation", {
        "found": bool(next_situation_match),
        "length": len(next_situation),
        "preview": next_situation[:50] + "..." if next_situation and len(next_situation) > 50 else next_situation
    })
    
    # Extract JSON modifications
    json_mods_match = re.search(r"JSON_MODIFICATIONS:\s*(.*?)(?=$)", response, re.DOTALL)
    json_mods_text = json_mods_match.group(1).strip() if json_mods_match else ""
    
    log_debug_info("Extracted JSON modifications text", {
        "found": bool(json_mods_match),
        "length": len(json_mods_text),
        "preview": json_mods_text[:50] + "..." if json_mods_text and len(json_mods_text) > 50 else json_mods_text
    })
    
    # Split the modifications into a list
    json_modifications = []
    if json_mods_text:
        # Extract items that start with a dash
        modifications = re.findall(r"- (.*?)(?=\n- |\n\n|$)", json_mods_text, re.DOTALL)
        json_modifications = [mod.strip() for mod in modifications if mod.strip()]
        
        log_debug_info("Parsed modifications", {
            "count": len(json_modifications),
            "items": json_modifications
        })
    
    return next_situation, json_modifications

def update_game_state(modifications: List[str]):
    """Update the game state based on the list of modifications"""
    log_debug_info("Updating game state with modifications", {"modification_count": len(modifications)})
    state = st.session_state['initial_state']
    
    for mod in modifications:
        try:
            log_debug_info("Processing modification", {"mod": mod})
            
            # Common modification patterns
            # Decrease resource
            decrease_match = re.search(r"decrease\s+resources\.(\w+)\s+by\s+(\d+)", mod, re.IGNORECASE)
            if decrease_match:
                resource, amount = decrease_match.groups()
                if resource in state.get("resources", {}):
                    state["resources"][resource] = max(0, state["resources"][resource] - int(amount))
                    log_debug_info(f"Decreased resource: {resource}", {
                        "amount": amount,
                        "new_value": state["resources"][resource]
                    })
                continue
                
            # Increase resource
            increase_match = re.search(r"increase\s+resources\.(\w+)\s+by\s+(\d+)", mod, re.IGNORECASE)
            if increase_match:
                resource, amount = increase_match.groups()
                if resource in state.get("resources", {}):
                    state["resources"][resource] = state["resources"][resource] + int(amount)
                else:
                    state["resources"][resource] = int(amount)
                log_debug_info(f"Increased resource: {resource}", {
                    "amount": amount,
                    "new_value": state["resources"][resource]
                })
                continue
                
            # Set resource value
            set_match = re.search(r"set\s+resources\.(\w+)\s+to\s+(\d+)", mod, re.IGNORECASE)
            if set_match:
                resource, amount = set_match.groups()
                if "resources" not in state:
                    state["resources"] = {}
                state["resources"][resource] = int(amount)
                log_debug_info(f"Set resource: {resource}", {
                    "amount": amount
                })
                continue
                
            # Update status
            status_match = re.search(r"update\s+status\s+to\s+[\"']?(.*?)[\"']?$", mod, re.IGNORECASE)
            if status_match:
                state["status"] = status_match.group(1).strip()
                log_debug_info("Updated status", {"new_status": state["status"]})
                continue
                
            # Add injury/condition to family member
            family_update_match = re.search(r"update\s+family\s+member\s+[\"']?(.*?)[\"']?\s+to\s+[\"']?(.*?)[\"']?$", mod, re.IGNORECASE)
            if family_update_match:
                # This is just storing a text description of the family update
                # In a more complex app, you would have a structured family members list
                if "family_status" not in state:
                    state["family_status"] = {}
                member, status = family_update_match.groups()
                state["family_status"][member.strip()] = status.strip()
                log_debug_info("Updated family member status", {
                    "member": member.strip(),
                    "new_status": status.strip()
                })
                continue
                
            # Add a new event or condition
            add_match = re.search(r"add\s+(\w+)\s+[\"']?(.*?)[\"']?$", mod, re.IGNORECASE)
            if add_match:
                category, value = add_match.groups()
                if category not in state:
                    state[category] = []
                if isinstance(state[category], list):
                    state[category].append(value.strip())
                    log_debug_info(f"Added item to {category}", {"value": value.strip()})
                continue
                
            # Generic key-value update
            kv_match = re.search(r"set\s+([\w\.]+)\s+to\s+[\"']?(.*?)[\"']?$", mod, re.IGNORECASE)
            if kv_match:
                key_path, value = kv_match.groups()
                keys = key_path.split('.')
                log_debug_info(f"Updating key path", {"path": key_path, "value": value})
                
                # Navigate to the nested dictionary
                current = state
                for i, key in enumerate(keys[:-1]):
                    if key not in current:
                        current[key] = {}
                    current = current[key]
                    
                # Set the value
                try:
                    # Try to convert to number if it looks like one
                    if value.isdigit():
                        current[keys[-1]] = int(value)
                    elif value.replace('.', '', 1).isdigit() and value.count('.') <= 1:
                        current[keys[-1]] = float(value)
                    else:
                        current[keys[-1]] = value
                except:
                    current[keys[-1]] = value
                    
            else:
                log_debug_info("No pattern match found for modification", {"mod": mod})
                
        except Exception as e:
            error_msg = f"Error applying modification: {mod}. Error: {str(e)}"
            log_debug_info(error_msg)
            log_debug_info("Exception traceback", traceback.format_exc())
            st.error(error_msg)
    
    # Increment day if not already done
    day_match = re.search(r"Day (\d+)", state.get("status", ""))
    if day_match and int(day_match.group(1)) == st.session_state['current_day']:
        state["status"] = f"Day {st.session_state['current_day'] + 1}"
        log_debug_info("Incremented day in status", {"new_status": state["status"]})
        
    st.session_state['initial_state'] = state
    st.session_state['current_day'] += 1
    log_debug_info("Updated current_day", {"new_value": st.session_state['current_day']})

def run_simulation():
    """Run the interactive simulation"""
    st.title(f"Crisis Simulation - {st.session_state['initial_state'].get('status', f'Day {st.session_state["current_day"]}')}") 
    log_debug_info("Entering run_simulation", {"current_day": st.session_state['current_day']})
    
    # Display the current situation
    st.subheader("Current Situation")
    st.write(st.session_state['latest_update'])
    
    # Display resources and status
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Resources")
        resources = st.session_state['initial_state'].get('resources', {})
        for resource, amount in resources.items():
            st.metric(label=resource.capitalize(), value=amount)
        log_debug_info("Displayed resources", resources)
    
    with col2:
        st.subheader("Family Status")
        family_status = st.session_state['initial_state'].get('family_status', {})
        if family_status:
            for member, status in family_status.items():
                st.write(f"**{member}**: {status}")
            log_debug_info("Displayed family status", family_status)
        else:
            st.write(f"Family members: {st.session_state['initial_state'].get('family', 'None')}")
            
        st.write(f"Vulnerabilities: {st.session_state['initial_state'].get('vulnerabilities', 'None')}")
    
    # User decision input
    st.subheader("Your Decision")
    user_action = st.text_area("What do you do next?", height=100)
    
    submit_button = st.button("Submit Decision")
    
    if submit_button and user_action:
        log_debug_info("Decision submitted", {"action_length": len(user_action)})
        
        with st.spinner("Processing your decision..."):
            # Prepare prompt for Mistral API
            recent_events = st.session_state['simulation_log'][-3:] if len(st.session_state['simulation_log']) > 3 else st.session_state['simulation_log']
            recent_events_text = "\n".join(recent_events)
            
            log_debug_info("Preparing prompt with recent events", {"events_count": len(recent_events)})
            
            prompt = f"""
            Current Simulation State (JSON):
            {json.dumps(st.session_state['initial_state'], indent=2)}
            
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
            
            # Call Mistral API
            log_debug_info("Calling Mistral API for decision processing")
            response = call_mistral_api(prompt)
            
            if response:
                log_debug_info("Received response from Mistral API", {"response_length": len(response)})
                
                # Parse the response
                next_situation, json_modifications = parse_mistral_response(response)
                
                if next_situation:
                    log_debug_info("Successfully parsed next situation", {"situation_length": len(next_situation)})
                    
                    # Update simulation log
                    st.session_state['simulation_log'].append(f"Your action: {user_action}")
                    st.session_state['simulation_log'].append(next_situation)
                    st.session_state['latest_update'] = next_situation
                    
                    log_debug_info("Updated simulation log", {
                        "log_length": len(st.session_state['simulation_log'])
                    })
                    
                    # Update game state
                    update_game_state(json_modifications)
                    
                    # Check if simulation should end
                    resources = st.session_state['initial_state'].get('resources', {})
                    
                    # End conditions: day > 10 or any critical resource at 0
                    if st.session_state['current_day'] > 10 or resources.get('food', 1) <= 0 or resources.get('water', 1) <= 0:
                        log_debug_info("Ending simulation", {
                            "reason": "day limit exceeded" if st.session_state['current_day'] > 10 else "critical resource depleted",
                            "current_day": st.session_state['current_day'],
                            "food": resources.get('food', 'N/A'),
                            "water": resources.get('water', 'N/A')
                        })
                        st.session_state['app_state'] = 'recap'
                    
                    st.rerun()
                else:
                    error_msg = "Failed to process your decision. Please try again."
                    log_debug_info(error_msg, {"next_situation_empty": True})
                    st.error(error_msg)
            else:
                error_msg = "Failed to process your decision. Please try again."
                log_debug_info(error_msg, {"api_response_empty": True})
                st.error(error_msg)

def generate_recap():
    """Generate and display the simulation recap"""
    st.title("Simulation Over")
    log_debug_info("Entering generate_recap")
    
    # Display the final state
    st.subheader("Final State")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Resources")
        resources = st.session_state['initial_state'].get('resources', {})
        for resource, amount in resources.items():
            st.metric(label=resource.capitalize(), value=amount)
        log_debug_info("Displayed final resources", resources)
    
    with col2:
        st.subheader("Family Status")
        family_status = st.session_state['initial_state'].get('family_status', {})
        if family_status:
            for member, status in family_status.items():
                st.write(f"**{member}**: {status}")
            log_debug_info("Displayed final family status", family_status)
        else:
            st.write(f"Family members: {st.session_state['initial_state'].get('family', 'None')}")
    
    # Display simulation log
    st.subheader("Simulation Timeline")
    for i, event in enumerate(st.session_state['simulation_log']):
        st.write(f"**Event {i+1}**: {event}")
    log_debug_info("Displayed simulation timeline", {"event_count": len(st.session_state['simulation_log'])})
    
    # Generate personalized advice
    st.subheader("Personalized Advice")
    
    if 'advice' not in st.session_state:
        log_debug_info("Generating personalized advice")
        with st.spinner("Generating personalized advice based on your simulation..."):
            prompt = f"""
            This user just completed a crisis simulation with the following:
            
            Initial Profile:
            {json.dumps(st.session_state['initial_state'].get('profile', {}), indent=2)}
            
            Final State:
            {json.dumps(st.session_state['initial_state'], indent=2)}
            
            Simulation Timeline:
            {json.dumps(st.session_state['simulation_log'], indent=2)}
            
            Based on how this simulation went, provide 3-5 practical, personalized pieces of advice to help this person prepare for a real crisis like the one simulated. Focus on specific actions they can take based on their location, vulnerabilities, and how the simulation played out.
            """
            
            advice = call_mistral_api(prompt)
            st.session_state['advice'] = advice
            log_debug_info("Received advice from API", {"advice_length": len(advice) if advice else 0})
    
    st.write(st.session_state['advice'])
    
    # User options
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Start a New Crisis"):
            log_debug_info("User selected 'Start a New Crisis'")
            # Reset all state except personal profile
            profile = st.session_state['initial_state'].get('profile', {})
            family = st.session_state['initial_state'].get('family', '')
            vulnerabilities = st.session_state['initial_state'].get('vulnerabilities', '')
            
            # Save debug info
            debug_info = st.session_state.get('debug_info', [])
            
            # Reset session state
            for key in list(st.session_state.keys()):
                if key != 'app_state':
                    del st.session_state[key]
            
            # Restore debug info
            st.session_state['debug_info'] = debug_info
            
            # Initialize with previous profile
            st.session_state['initial_state'] = {
                "profile": profile,
                "family": family,
                "vulnerabilities": vulnerabilities
            }
            
            log_debug_info("Resetting for new crisis", {
                "preserved_profile": profile,
                "preserved_family": family,
                "preserved_vulnerabilities": vulnerabilities
            })
            
            st.session_state['app_state'] = 'generating_scenario'
            st.rerun()
    
    with col2:
        if st.button("Start From Scratch"):
            log_debug_info("User selected 'Start From Scratch'")
            
            # Save debug info
            debug_info = st.session_state.get('debug_info', [])
            
            # Reset all state
            for key in list(st.session_state.keys()):
                if key != 'app_state':
                    del st.session_state[key]
            
            # Restore debug info
            st.session_state['debug_info'] = debug_info
            
            st.session_state['app_state'] = 'collecting_info'
            log_debug_info("Complete reset to collecting_info state")
            st.rerun()

def display_debug_panel():
    """Display debug information in a collapsible panel"""
    with st.expander("Debug Information", expanded=False):
        st.subheader("Application State")
        st.json({
            "app_state": st.session_state.get('app_state', 'Not set'),
            "current_day": st.session_state.get('current_day', 'Not set'),
            "log_entries": len(st.session_state.get('simulation_log', [])),
            "profile": st.session_state.get('initial_state', {}).get('profile', 'Not set')
        })
        
        st.subheader("API Configuration")
        api_key_status = "Set in secrets" if st.secrets.get("MISTRAL_API_KEY") else "Missing in secrets"
        api_key_env_status = "Set in environment" if os.environ.get("MISTRAL_API_KEY") else "Missing in environment"
        
        st.write(f"Mistral API Key: {api_key_status}, {api_key_env_status}")
        
        st.subheader("Debug Log")
        if 'debug_info' in st.session_state and st.session_state['debug_info']:
            for entry in st.session_state['debug_info'][-20:]:  # Show last 20 entries
                with st.container():
                    st.write(f"**[{entry['timestamp']}]** {entry['message']}")
                    if entry.get('data'):
                        with st.expander("Details", expanded=False):
                            st.json(entry['data'])
        else:
            st.write("No debug information available")
        
        st.button("Clear Debug Log", on_click=lambda: st.session_state.update({'debug_info': []}))

def main():
    """Main application function"""
    st.set_page_config(
        page_title="Crisis Simulation",
        page_icon="🚨",
        layout="wide"
    )
    
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    log_debug_info("Application started")
    
    # Initialize session state
    initialize_session_state()
    
    # Debug panel at the top
    display_debug_panel()
    
    # Render the appropriate view based on app state
    log_debug_info(f"Current app_state: {st.session_state['app_state']}")
    
    try:
        if st.session_state['app_state'] == 'collecting_info':
            render_input_form()
        elif st.session_state['app_state'] == 'generating_scenario':
            generate_crisis_scenario()
        elif st.session_state['app_state'] == 'in_simulation':
            run_simulation()
        elif st.session_state['app_state'] == 'recap':
            generate_recap()
        else:
            log_debug_info(f"Unknown app_state: {st.session_state['app_state']}")
            st.error(f"Unknown application state: {st.session_state['app_state']}")
            if st.button("Reset Application"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
    except Exception as e:
        error_msg = f"An unexpected error occurred: {str(e)}"
        log_debug_info(error_msg)
        log_debug_info("Exception traceback", traceback.format_exc())
        st.error(error_msg)
        st.code(traceback.format_exc())
        
        if st.button("Reset Application"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

if __name__ == "__main__":
    main()