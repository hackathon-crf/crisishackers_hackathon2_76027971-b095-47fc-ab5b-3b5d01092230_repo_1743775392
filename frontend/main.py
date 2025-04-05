import streamlit as st
from pathlib import Path
from frontend.middleware import call_backend_test
from frontend.chatbot import initialize_session_state as initialize_chatbot
from frontend.chatbot import add_message

def render_chatbot():
    """Render the chatbot interface"""
    st.header("Mistral AI Chatbot")
    
    # Initialize session state
    initialize_chatbot()
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Get user input
    user_input = st.chat_input("Type your message here...")
    
    if user_input:
        # Add user message to conversation
        add_message("user", user_input)
        
        # Display user message
        with st.chat_message("user"):
            st.write(user_input)
        
        # Get response from backend
        from frontend.middleware import call_chat_endpoint
        
        with st.spinner("Thinking..."):
            response_data = call_chat_endpoint(st.session_state.conversation_history)
            
            if response_data and response_data.get("status") == 200:
                assistant_response = response_data.get("data", {}).get("response", "")
                
                # Add assistant response to conversation
                add_message("assistant", assistant_response)
                
                # Display assistant response
                with st.chat_message("assistant"):
                    st.write(assistant_response)
            else:
                error_msg = response_data.get("message", "Failed to get response from AI") if response_data else "Failed to connect to backend"
                st.error(error_msg)
                st.write("Debug info:")
                st.json(response_data)

def render_crisis_simulation():
    """Render the crisis simulation UI by importing and running its main function"""
    # Use the updated crisis simulation with backend integration
    from frontend.crisis_simulation_updated import main as crisis_simulation_main
    crisis_simulation_main()

def main():
    # Create sidebar buttons
    st.sidebar.title("Crisou")
    #selected_page = st.sidebar.radio("Go to", ["Default App", "Chatbot", "Crisis Simulation", "README"])
    
    
    render_crisis_simulation()
            
 