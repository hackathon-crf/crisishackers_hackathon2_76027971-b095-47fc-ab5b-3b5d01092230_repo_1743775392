import streamlit as st
import json
import re
import logging
import os
import sys
import traceback
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from frontend.middleware import (
    call_crisis_scenario, call_crisis_decision, call_crisis_advice
)

# Configure logging
os.makedirs("logs", exist_ok=True)
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

def render_input_form():
    """Render the form to collect user information"""
    st.title("Crisis Simulation")


    st.write("Crisou est un jeu éducatif immersif qui sensibilise le grand public aux gestes essentiels à adopter face aux situations de crise, comme les inondations. À travers un parcours interactif et des choix stratégiques, le joueur accompagne un petit avatar dans sa quête de survie. Chaque décision compte : bien répondre aux questions permet de guider le personnage vers la sécurité.")
    st.subheader("Please provide information about yourself to generate a personalized crisis scenario.")
    
    with st.form("user_info_form"):
        name = st.text_input("Your Name")
        age = st.number_input("Your Age", min_value=1, max_value=120, value=30)
        location = st.text_input("Your Current Location (be specific - City/Region/Country)")
        profile_options = ("Boss", "Employee") # Using a tuple is common for fixed options

        # Use st.selectbox to create the dropdown
        profile = st.selectbox(
            label="Select Profile Type:",  # Clearer label for selection
            options=profile_options,
            index=0,  # Optional: Sets the default selection to the first item ("Boss")
            # index=None # Optional: Use this if you want no default selection initially
            key='profile_selection' # Optional: A unique key is good practice, especially in forms
        )
        description = st.text_area("Professional environment")
        #vulnerabilities = st.text_area("Vulnerabilities (e.g., 'Child has asthma, limited savings, live on 3rd floor apartment')")
        
        submit_button = st.form_submit_button("Start Simulation")
        
        if submit_button:
            log_debug_info("Form submitted", {
                "name": name,
                "age": age,
                "location": location,
                "profile": profile,
                "description": description
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
                "profile": profile,
                "description": description,
                "status": "Day 1"
            }
            
            log_debug_info("Updated initial_state", st.session_state['initial_state'])
            log_debug_info("Changing app_state to 'generating_scenario'")
            st.session_state['app_state'] = 'generating_scenario'
            st.rerun()

def generate_crisis_scenario():
    """Generate the initial crisis scenario using the backend API"""
    st.title("Generating Crisis Scenario")
    log_debug_info("Entering generate_crisis_scenario")
    
    with st.spinner("Generating a personalized crisis scenario based on your location and information..."):
        log_debug_info("Calling backend API for crisis scenario generation")
        
        response = call_crisis_scenario(st.session_state['initial_state'])
        
        if response and response.get("status") == 200:
            scenario_description = response.get("data", {}).get("scenario", "")
            
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
                error_msg = "Empty scenario returned from API"
                log_debug_info(error_msg)
                st.error(error_msg)
                st.button("Try Again", on_click=lambda: None)
        else:
            error_msg = "Failed to generate a crisis scenario. Please try again."
            log_debug_info(error_msg, {"response": response})
            st.error(error_msg)
            if response:
                st.write("API Response:")
                st.json(response)
            st.button("Try Again", on_click=lambda: None)

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
    #st.title(f"Crisis Simulation - {st.session_state['initial_state'].get('status', f'Day {st.session_state["current_day"]}')}") 
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
            # Prepare data for API call
            recent_events = st.session_state['simulation_log'][-3:] if len(st.session_state['simulation_log']) > 3 else st.session_state['simulation_log']
            
            log_debug_info("Calling backend API for decision processing", {"events_count": len(recent_events)})
            
            request_data = {
                "state": st.session_state['initial_state'],
                "user_action": user_action,
                "recent_events": recent_events
            }
            
            response = call_crisis_decision(request_data)
            
            if response and response.get("status") == 200:
                data = response.get("data", {})
                next_situation = data.get("next_situation", "")
                json_modifications = data.get("json_modifications", [])
                
                log_debug_info("Received API response", {
                    "next_situation_length": len(next_situation),
                    "modifications_count": len(json_modifications)
                })
                
                if next_situation:
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
                    error_msg = "Empty situation returned from API"
                    log_debug_info(error_msg)
                    st.error(error_msg)
                    st.write("API Response:")
                    st.json(response)
            else:
                error_msg = "Failed to process your decision. Please try again."
                log_debug_info(error_msg, {"response": response})
                st.error(error_msg)
                if response:
                    st.write("API Response:")
                    st.json(response)

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
        log_debug_info("Calling backend API for personalized advice")
        with st.spinner("Generating personalized advice based on your simulation..."):
            request_data = {
                "profile": st.session_state['initial_state'].get('profile', {}),
                "final_state": st.session_state['initial_state'],
                "simulation_log": st.session_state['simulation_log']
            }
            
            response = call_crisis_advice(request_data)
            
            if response and response.get("status") == 200:
                advice = response.get("data", {}).get("advice", "")
                st.session_state['advice'] = advice
                log_debug_info("Received advice from API", {"advice_length": len(advice) if advice else 0})
            else:
                st.session_state['advice'] = "Unable to generate personalized advice. Please try again."
                log_debug_info("Failed to get advice from API", {"response": response})
                if response:
                    st.write("API Response:")
                    st.json(response)
    
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
        # Check if logs directory exists
        if os.path.exists("logs/middleware.log"):
            with open("logs/middleware.log", "r") as f:
                # Get last 5 lines
                last_lines = f.readlines()[-5:]
                st.code("".join(last_lines), language="text")
        
        st.subheader("Debug Log")
        if 'debug_info' in st.session_state and st.session_state['debug_info']:
            for entry in st.session_state['debug_info'][-20:]:  # Show last 20 entries
                with st.container():
                    st.write(f"**[{entry['timestamp']}]** {entry['message']}")
                    #if entry.get('data'):
                    #    with st.expander("Details", expanded=False):
                    #        st.json(entry['data'])
        else:
            st.write("No debug information available")
        
        st.button("Clear Debug Log", on_click=lambda: st.session_state.update({'debug_info': []}))

def main():
    """Main application function"""
    
    
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    log_debug_info("Application started")
    
    # Initialize session state
    initialize_session_state()
    
    # Debug panel at the top
    #display_debug_panel()
    
    # Render the appropriate view based on app state
    log_debug_info(f"Current app_state: {st.session_state['app_state']}")
    st.title("Crisou")
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