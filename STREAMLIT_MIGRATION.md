# Frontend Migration to Streamlit

This document describes the migration of the frontend from Next.js/React to Streamlit.

## Overview

The frontend has been migrated from Next.js/React (TypeScript) to Streamlit (Python). The Streamlit frontend communicates with the Python FastAPI backend via HTTP API.

## Frontend Structure

The Streamlit frontend is located in the `frontend/` directory:

```
frontend/
├── app.py                 # Main Streamlit application entry point
├── requirements.txt       # Python dependencies
├── pages/                 # Page modules
│   ├── chat.py           # Chat interface
│   └── tools_panel.py    # Tools configuration panel
├── utils/                 # Utility modules
│   ├── state.py          # Session state management
│   └── streaming.py      # Streaming utilities
├── lib/                  # Library code
│   └── assistant.py      # Message processing and streaming
└── config/               # Configuration
    └── constants.py      # Constants
```

## Setup Instructions

### 1. Install Python Dependencies

```bash
cd frontend
pip install -r requirements.txt
```

### 2. Set Environment Variables

Set the API base URL (or use default):

```bash
export API_BASE_URL=http://localhost:8000
```

Or create a `.env` file:

```bash
API_BASE_URL=http://localhost:8000
```

### 3. Run the Streamlit App

```bash
cd frontend
streamlit run app.py
```

The app will be available at `http://localhost:8501`.

### 4. Ensure Backend is Running

Make sure the Python backend is running (see `backend/README.md`):

```bash
cd backend
uvicorn main:app --reload --port 8000
```

## Features

### Chat Interface

- Real-time chat with the assistant
- Streaming responses
- Message history
- Tool call visualization
- Annotations display

### Tools Panel (Sidebar)

- **File Search**: Upload files and manage vector stores
- **Web Search**: Configure location-based search
- **Code Interpreter**: Enable Python code execution
- **Functions**: Enable custom functions (weather, joke)
- **MCP**: Configure MCP server connections
- **Google Integration**: OAuth integration for Gmail and Calendar

## Differences from React Frontend

1. **State Management**: Uses Streamlit's `st.session_state` instead of Zustand
2. **UI Components**: Uses Streamlit's built-in components instead of React components
3. **Rendering**: Server-side rendering with automatic reruns instead of client-side React
4. **Streaming**: Handles streaming responses through HTTP streaming
5. **Layout**: Uses Streamlit's column and sidebar layout instead of CSS Grid/Flexbox

## Usage Flow

1. Start the Python backend: `cd backend && uvicorn main:app --reload --port 8000`
2. Start the Streamlit frontend: `cd frontend && streamlit run app.py`
3. Configure tools in the sidebar
4. Start chatting with the assistant

## Key Components

### Chat Interface (`pages/chat.py`)

- Displays chat messages
- Handles user input
- Processes streaming responses
- Renders tool calls and annotations

### Tools Panel (`pages/tools_panel.py`)

- File upload and vector store management
- Web search configuration
- MCP server configuration
- Google OAuth integration

### Message Processing (`lib/assistant.py`)

- Handles SSE (Server-Sent Events) streaming
- Processes different event types
- Updates session state in real-time
- Manages conversation flow

## Notes

- Streamlit automatically reruns the app when session state changes
- Streaming responses update the UI in real-time
- File uploads are handled through Streamlit's file uploader
- Google OAuth redirects to a new tab (handled by backend)
- Session state persists during the Streamlit session

## Troubleshooting

1. **Backend Connection Error**: Ensure the backend is running and `API_BASE_URL` is correct
2. **Streaming Not Working**: Check that the backend supports streaming responses
3. **State Not Persisting**: Streamlit session state only persists during the session
4. **File Upload Issues**: Check file size limits and backend file handling

## Production Deployment

For production:

1. Use Streamlit Cloud or deploy to a server
2. Set up proper environment variables
3. Configure CORS on the backend for your domain
4. Use HTTPS for secure connections
5. Set up proper session management if needed
6. Consider using Streamlit's authentication features

