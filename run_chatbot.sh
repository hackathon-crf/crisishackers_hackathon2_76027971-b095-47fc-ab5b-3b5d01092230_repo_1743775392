#!/bin/bash

# Start the backend server
echo "Starting the backend server..."
cd "$(dirname "$0")"
python main_back.py --port 1027 > logs/backend.log 2>&1 &
BACKEND_PID=$!

# Wait for the backend to start up
echo "Waiting for backend to start..."
sleep 3

# Start the Streamlit frontend
echo "Starting the Streamlit frontend..."
streamlit run main_front.py

# When Streamlit is closed, stop the backend
echo "Stopping the backend server..."
kill $BACKEND_PID