# Streamlit Secrets Configuration

This guide explains how to configure API keys and secrets for the application using Streamlit's secrets management.

## Setup Streamlit Secrets

### Local Development

1. **Create the secrets directory:**
```bash
mkdir -p .streamlit
```

2. **Create `secrets.toml` file:**
```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

3. **Edit `.streamlit/secrets.toml`** and add your actual API keys:

```toml
# OpenAI API Key (required)
OPENAI_API_KEY = "sk-your-actual-openai-api-key-here"

# Google OAuth Configuration (optional)
GOOGLE_CLIENT_ID = "your-google-client-id.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "your-google-client-secret"
GOOGLE_REDIRECT_URI = "http://localhost:8501/api/google/callback"

# API Base URL (for frontend)
API_BASE_URL = "http://localhost:8000"

# Environment
NODE_ENV = "development"
```

### Streamlit Cloud Deployment

1. **Go to your Streamlit Cloud app settings**
2. **Navigate to "Secrets"**
3. **Add secrets** in TOML format:

```toml
OPENAI_API_KEY = "sk-your-actual-openai-api-key-here"
GOOGLE_CLIENT_ID = "your-google-client-id"
GOOGLE_CLIENT_SECRET = "your-google-client-secret"
GOOGLE_REDIRECT_URI = "https://your-app.streamlit.app/api/google/callback"
API_BASE_URL = "https://your-backend-url.com"
NODE_ENV = "production"
```

## How It Works

### Backend (FastAPI)

The backend uses `lib/config.py` which:
1. **First tries** to read from Streamlit secrets (`st.secrets`) if Streamlit is available
2. **Falls back** to environment variables (`os.getenv()`) if Streamlit is not available

This allows the backend to work:
- ✅ Standalone (using environment variables)
- ✅ When called from Streamlit (using Streamlit secrets)
- ✅ In production (using environment variables or Streamlit Cloud secrets)

### Frontend (Streamlit)

The Streamlit frontend can access secrets directly using `st.secrets`:

```python
import streamlit as st

# Access secrets
api_key = st.secrets["OPENAI_API_KEY"]
api_url = st.secrets.get("API_BASE_URL", "http://localhost:8000")
```

## Security Best Practices

1. **Never commit `secrets.toml` to git**
   - Add `.streamlit/secrets.toml` to `.gitignore`
   - Only commit `secrets.toml.example` as a template

2. **Use different keys for development and production**
   - Local: Use `secrets.toml` file
   - Production: Use Streamlit Cloud secrets or environment variables

3. **Rotate keys regularly**
   - Update secrets in Streamlit Cloud
   - Update local `secrets.toml` file

4. **Limit access**
   - Only share secrets with trusted team members
   - Use least privilege principle

## Troubleshooting

### "OPENAI_API_KEY not found" error

1. **Check if secrets file exists:**
   ```bash
   ls -la .streamlit/secrets.toml
   ```

2. **Verify the key name:**
   - Should be `OPENAI_API_KEY` (uppercase)
   - Check for typos

3. **Check if backend can access secrets:**
   - Backend tries Streamlit secrets first, then environment variables
   - Make sure at least one is set

### Backend can't read Streamlit secrets

- **Normal behavior**: Backend runs separately from Streamlit
- **Solution**: Use environment variables for backend, or ensure Streamlit secrets are accessible
- **Alternative**: Pass API keys via environment variables when starting backend

### Secrets not updating

- **Streamlit**: Restart the Streamlit app after changing secrets
- **Backend**: Restart the backend server after changing environment variables

## Example: Running with Secrets

### Development Setup

**Terminal 1 - Backend:**
```bash
cd backend
# Uses environment variables or Streamlit secrets if available
uvicorn main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
# Uses Streamlit secrets from .streamlit/secrets.toml
streamlit run app.py
```

### Production Setup

**Backend (using environment variables):**
```bash
export OPENAI_API_KEY="sk-..."
export GOOGLE_CLIENT_ID="..."
export GOOGLE_CLIENT_SECRET="..."
uvicorn main:app --host 0.0.0.0 --port 8000
```

**Frontend (Streamlit Cloud):**
- Configure secrets in Streamlit Cloud dashboard
- Secrets are automatically available via `st.secrets`

