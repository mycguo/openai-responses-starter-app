# Backend Migration to Python

This document describes the migration of the backend from Next.js API routes to a Python FastAPI backend.

## Overview

The backend has been migrated from Next.js API routes (TypeScript) to a Python FastAPI application. The frontend remains in Next.js/React and can be configured to use either the original Next.js API routes or the new Python backend.

## Backend Structure

The Python backend is located in the `backend/` directory:

```
backend/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── api/                    # API route handlers
│   ├── turn_response.py   # Main streaming endpoint
│   ├── google_auth.py     # Google OAuth initiation
│   ├── google_callback.py # Google OAuth callback
│   ├── google_status.py   # Google OAuth status
│   ├── vector_stores.py   # Vector store operations
│   ├── functions.py       # Function endpoints (weather, joke)
│   └── container_files.py # Container file content
├── lib/                    # Library code
│   ├── session.py         # Session management
│   ├── connectors_auth.py # OAuth token handling
│   └── tools.py           # Tools configuration
└── config/                 # Configuration
    ├── constants.py       # Constants and prompts
    └── tools_list.py      # Available tools list
```

## Setup Instructions

### 1. Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Set Environment Variables

Create a `.env` file in the `backend/` directory (or set environment variables):

```bash
OPENAI_API_KEY=your_openai_api_key
GOOGLE_CLIENT_ID=your_google_client_id  # Optional
GOOGLE_CLIENT_SECRET=your_google_client_secret  # Optional
GOOGLE_REDIRECT_URI=http://localhost:3000/api/google/callback  # Optional
NODE_ENV=development  # or production
```

### 3. Run the Python Backend

```bash
cd backend
uvicorn main:app --reload --port 8000
```

The backend will be available at `http://localhost:8000`.

### 4. Configure Frontend to Use Python Backend

Create or update `.env.local` in the project root:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

If `NEXT_PUBLIC_API_URL` is not set, the frontend will use the Next.js API routes (original behavior).

### 5. Run the Frontend

```bash
npm install
npm run dev
```

The frontend will be available at `http://localhost:3000`.

## API Endpoints

All endpoints maintain the same paths as the original Next.js API routes:

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

## Differences from Original Implementation

1. **Session Management**: Currently uses in-memory storage. For production, consider using Redis or a database.

2. **OpenAI SDK**: The Python OpenAI SDK uses synchronous methods, but FastAPI handles this correctly with async/await.

3. **CORS**: Configured to allow requests from `http://localhost:3000`. Update for production.

4. **Error Handling**: All endpoints return proper JSON error responses with appropriate status codes.

5. **Streaming**: The streaming endpoint uses Python generators to stream SSE (Server-Sent Events) data.

## Migration Notes

- The frontend code has been updated to use a configurable `API_BASE_URL` from `lib/api-config.ts`
- All API calls now use `${API_BASE_URL}/api/...` instead of hardcoded `/api/...`
- The original Next.js API routes remain in `app/api/` and can still be used if `NEXT_PUBLIC_API_URL` is not set
- Google OAuth flow has been fully migrated to Python with PKCE support
- Vector store operations maintain the same API contract

## Testing

1. Start the Python backend: `cd backend && uvicorn main:app --reload --port 8000`
2. Set `NEXT_PUBLIC_API_URL=http://localhost:8000` in `.env.local`
3. Start the frontend: `npm run dev`
4. Test all features:
   - Chat conversations
   - Web search
   - File search with vector stores
   - Code interpreter
   - Functions (weather, joke)
   - Google OAuth integration

## Production Deployment

For production:

1. Use a production ASGI server like Gunicorn with Uvicorn workers
2. Set up proper session storage (Redis recommended)
3. Configure CORS for your production domain
4. Use environment variables for all secrets
5. Set up proper logging and monitoring
6. Consider using a reverse proxy (nginx) in front of the FastAPI app

