# Mistral AI Chatbot

This project implements a simple chatbot using the Mistral AI API in two formats:
1. A command-line interface (CLI)
2. A web interface using Streamlit and FastAPI

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Mistral API Key**:
   - Copy `.env.example` to `.env`
   - Edit `.env` and add your Mistral API key
   - For Streamlit interface, also add your key to `.streamlit/secrets.toml`

## Command-Line Interface

The CLI version provides a simple text-based interface for interacting with the Mistral AI model.

### Usage

```bash
# Run with default settings
./chatbot.py

# Run with a specific model
./chatbot.py --model mistral-medium-latest

# Run with custom history size
./chatbot.py --max-history 5
```

### Commands
- Type your message and press Enter to get a response
- Type `exit` or `quit` to end the conversation
- Type `clear` to clear the conversation history

## Web Interface

The web interface provides a more user-friendly way to interact with the chatbot using Streamlit for the frontend and FastAPI for the backend.

### Running the Web Interface

1. **Start the backend**:
   ```bash
   python main_back.py --port 1027 --baseurl "http://localhost"
   ```

2. **Start the frontend**:
   ```bash
   streamlit run main_chatbot.py
   ```

3. **Access the web interface**:
   Open your browser and navigate to `http://localhost:8501`

## Architecture

- **Backend**: FastAPI application handling API calls to Mistral
- **Frontend**: 
  - CLI: Simple Python script for command-line interaction
  - Web: Streamlit application for web-based interaction
- **Communication**: REST API endpoints for frontend-backend communication

## API Endpoints

- `POST /api/app/chat/`: Send conversation history and get AI response

## Configuration

- **Environment Variables**:
  - `MISTRAL_API_KEY`: Your Mistral API key
  - `DOMAIN_NAME`: Domain name for backend (default: localhost)
  - `ROOT_PATH`: Root path for API (default: empty)
  - `BACKEND_PORT`: Port for backend (default: 8090)

## Extending the Chatbot

The chatbot can be extended in several ways:
- Add system prompts to give the chatbot a specific personality
- Implement streaming responses for better user experience
- Add message persistence for preserving conversations
- Integrate with external data sources for enhanced knowledge