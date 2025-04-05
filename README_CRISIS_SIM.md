# Crisis Simulation Application

This interactive simulation guides users through personalized crisis scenarios, dynamically generated and evolved using the Mistral AI API. The application helps users prepare for potential crisis situations specific to their location and circumstances.

## Features

- Personalized crisis scenarios based on user location and profile
- Dynamic scenario evolution based on user decisions
- Resource and status tracking
- Simulation recap with personalized advice
- Interactive Streamlit interface
- Extensive debugging and logging
- FastAPI backend integration

## Architecture

- **Frontend**: Streamlit interface in `/frontend/crisis_simulation_updated.py`
- **Backend**: FastAPI services in `/backend/app/services.py` and `/backend/app/routes.py`
- **API Endpoints**:
  - `/api/app/crisis/scenario`: Generate initial crisis scenario
  - `/api/app/crisis/decision`: Process user decisions
  - `/api/app/crisis/advice`: Generate personalized advice
- **Middleware**: Communication layer in `/frontend/middleware.py`

## Setup Instructions

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Configure your Mistral API key:
   - Copy `.env.example` to `.env`
   - Edit `.env` and add your actual Mistral API key
   - Get your API key from [Mistral AI Console](https://console.mistral.ai/)

3. Test your Mistral API connection:
   ```
   ./test_mistral_api.py
   ```

4. Run the application:
   ```
   # Start backend server (in one terminal)
   python main_back.py
   
   # Start frontend (in another terminal)
   streamlit run main_front.py
   ```
   
5. Navigate to "Crisis Simulation" in the sidebar menu

## Troubleshooting

If the application isn't working correctly:

1. Check the debug panel in the Crisis Simulation UI (expandable section at the top)
2. Verify logs in the `logs/` directory:
   - `crisis_simulation.log`: Frontend logs
   - `middleware.log`: API communication logs
   - `services.log`: Backend service logs
3. Ensure your API key is correctly set in `.env`
4. Check network connectivity between frontend and backend
5. Verify backend is running by checking the test endpoint `/api/app/test/`

## How It Works

1. **Initial Setup**: The user provides personal information, including name, age, location, family members, and vulnerabilities.

2. **Scenario Generation**: The frontend calls the `/api/app/crisis/scenario` endpoint, which uses the Mistral API to generate a personalized crisis scenario based on the user's location and profile.

3. **Interactive Simulation**: The user makes decisions that are sent to the `/api/app/crisis/decision` endpoint for processing. The backend returns the next situation description and state modifications.

4. **Simulation Recap**: At the conclusion, the frontend calls `/api/app/crisis/advice` to generate personalized advice based on the simulation results.

## Additional Notes

- The application uses Streamlit's session state to maintain user data and progress
- Crisis scenarios are tailored to be realistic based on the user's location
- Resource management is a key aspect of the simulation
- The simulation typically ends after 10 days or when critical resources are depleted