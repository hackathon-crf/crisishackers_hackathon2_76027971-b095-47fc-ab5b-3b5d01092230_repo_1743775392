# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build/Run Commands
- Start backend: `python main_back.py --port 1027 --baseurl "http://localhost"`
- Start frontend: `streamlit run main_front.py`
- Start both: `./start.sh`
- Install dependencies: `pip install -r requirements.txt`

## Directory Structure
- Do not rename or delete existing directories
- Backend logic in `main_back.py` and `/backend`
- Frontend logic in `main_front.py` and `/frontend`
- Configuration in `/settings/config.py`

## Code Style Guidelines
- **Imports**: Standard imports first, third-party second, local imports last
- **Typing**: Use type annotations (Pydantic models and function signatures)
- **Naming**: snake_case for functions/variables, CamelCase for classes, UPPER_CASE for constants
- **Error handling**: Use specific try/except blocks with detailed error messages
- **Documentation**: DocStrings for functions (see `create_app` in routes.py)
- **Config Management**: Use .client_env and settings/config.py for configuration

## Config.toml Guidelines
- Avoid modifying the [server] block if possible
- If [server] block is necessary, add it at the end of config.toml