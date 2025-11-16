# Python Backend for OpenAI Responses Starter App

This is the Python FastAPI backend for the OpenAI Responses Starter App.

## Setup

1. **Install dependencies:**

```bash
pip install -r requirements.txt
```

2. **Set API keys:**

The backend supports multiple methods for providing API keys:

### Option A: Streamlit Secrets (Recommended for Streamlit deployment)

Create `.streamlit/secrets.toml` file in the project root:

```toml
OPENAI_API_KEY = "your_openai_api_key"
GOOGLE_CLIENT_ID = "your_google_client_id"  # Optional
GOOGLE_CLIENT_SECRET = "your_google_client_secret"  # Optional
GOOGLE_REDIRECT_URI = "http://localhost:8501/api/google/callback"  # Optional
NODE_ENV = "development"  # or production
```

### Option B: Environment Variables

Create a `.env` file in the `backend` directory (or set environment variables):

```bash
OPENAI_API_KEY=your_openai_api_key
GOOGLE_CLIENT_ID=your_google_client_id  # Optional, for Google integration
GOOGLE_CLIENT_SECRET=your_google_client_secret  # Optional, for Google integration
GOOGLE_REDIRECT_URI=http://localhost:8501/api/google/callback  # Optional
NODE_ENV=development  # or production
```

**Priority:** Streamlit secrets > Environment variables

3. **Run the backend:**

Navigate to the `backend` directory and run:

```bash
cd backend

# Option 1: Using uvicorn (recommended for development)
uvicorn main:app --reload --port 8000

# Option 2: Using Python directly
python main.py
```

The backend will be available at `http://localhost:8000`.

**Quick Start:**
```bash
# From project root
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

## API Endpoints

- `POST /api/turn_response` - Main streaming endpoint for chat responses
- `GET /api/google/auth` - Initiate Google OAuth flow
- `GET /api/google/callback` - Handle Google OAuth callback
- `GET /api/google/status` - Get Google OAuth connection status
- `POST /api/vector_stores/create_store` - Create a vector store
- `GET /api/vector_stores/list_files` - List files in a vector store
- `GET /api/vector_stores/retrieve_store` - Retrieve a vector store
- `POST /api/vector_stores/add_file` - Add a file to a vector store
- `POST /api/vector_stores/upload_file` - Upload a file to OpenAI
- `GET /api/functions/get_weather` - Get weather for a location
- `GET /api/functions/get_joke` - Get a programming joke
- `GET /api/container_files/content` - Get container file content

## Configuration

The backend uses `lib/config.py` to manage secrets. It supports:

1. **Streamlit Secrets**: If Streamlit is available, reads from `st.secrets`
2. **Environment Variables**: Falls back to `os.getenv()`

This allows the backend to work:
- Standalone (using environment variables)
- When called from Streamlit (using Streamlit secrets)
- In production (using environment variables or Streamlit Cloud secrets)

## Notes

- Session management is currently in-memory. For production, use Redis or a database.
- CORS is configured to allow requests from `http://localhost:3000` (Next.js) and `http://localhost:8501` (Streamlit). Update this for production.
- The OpenAI Python SDK uses synchronous methods, but FastAPI handles this with async/await.
