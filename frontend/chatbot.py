import streamlit as st
from typing import List, Dict, Any
from frontend.middleware import call_chat_endpoint

def initialize_session_state():
    """Initialize session state variables if they don't exist"""
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []

def add_message(role: str, content: str):
    """Add a message to both the conversation history and the display messages"""
    # Add to API conversation history
    st.session_state.conversation_history.append({"role": role, "content": content})
    
    # Add to display messages
    st.session_state.messages.append({"role": role, "content": content})

def main():
    """Main function for the Streamlit chatbot application"""
    st.set_page_config(
        page_title="Mistral Chatbot",
        page_icon="💬"
    )
    
    st.title("Mistral AI Chatbot")
    
    # Initialize session state
    initialize_session_state()
    
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
        
        # Get response from API
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

if __name__ == "__main__":
    main()