# Streamlit Frontend

This is the Streamlit frontend for the OpenAI Responses Starter App.

## Setup

1. **Install dependencies:**

```bash
pip install -r requirements.txt
```

2. **Set API keys and configuration:**

### Option A: Streamlit Secrets (Recommended)

Create `.streamlit/secrets.toml` file in the project root:

```toml
# API Configuration
API_BASE_URL = "http://localhost:8000"

# OpenAI API Key (required - backend will use this)
OPENAI_API_KEY = "your_openai_api_key"

# Google OAuth Configuration (optional)
GOOGLE_CLIENT_ID = "your_google_client_id"
GOOGLE_CLIENT_SECRET = "your_google_client_secret"
GOOGLE_REDIRECT_URI = "http://localhost:8501/api/google/callback"

# Environment
NODE_ENV = "development"
```

### Option B: Environment Variables

Set environment variables:

```bash
export API_BASE_URL=http://localhost:8000
export OPENAI_API_KEY=your_openai_api_key
```

**Note:** The backend will automatically read from Streamlit secrets if available, or fall back to environment variables.

3. **Run the Streamlit app:**

```bash
streamlit run app.py
```

The app will be available at `http://localhost:8501`.

## Features

- **Chat Interface**: Interactive chat with the assistant
- **Tools Panel**: Configure all available tools:
  - File Search with vector stores
  - Web Search with location configuration
  - Code Interpreter
  - Functions (weather, joke)
  - MCP server configuration
  - Google OAuth integration

## Usage

1. Start the Python backend (see `backend/README.md`)
2. Start the Streamlit frontend: `streamlit run app.py`
3. Configure tools in the sidebar
4. Start chatting!

## Notes

- The frontend communicates with the Python backend via HTTP API
- Streaming responses are handled in real-time
- Session state is managed by Streamlit's built-in session state
- File uploads are handled through Streamlit's file uploader component

