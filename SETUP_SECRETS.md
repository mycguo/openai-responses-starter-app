# Setting Up Secrets

## Option 1: User Home Directory (Recommended for Global Secrets)

Create `~/.streamlit/secrets.toml`:

```bash
mkdir -p ~/.streamlit
```

Then create/edit `~/.streamlit/secrets.toml`:

```toml
# API Configuration
API_BASE_URL = "http://localhost:8000"

# OpenAI API Key (required)
OPENAI_API_KEY = "your_openai_api_key"

# Google OAuth Configuration (optional)
GOOGLE_CLIENT_ID = "your_google_client_id"
GOOGLE_CLIENT_SECRET = "your_google_client_secret"
GOOGLE_REDIRECT_URI = "http://localhost:8501/api/google/callback"

# Environment
NODE_ENV = "development"
```

## Option 2: Project Directory

Create `.streamlit/secrets.toml` in the project root:

```bash
mkdir -p .streamlit
```

Then create/edit `.streamlit/secrets.toml` with the same content as above.

## Option 3: Environment Variables

Set environment variables:

```bash
export GOOGLE_CLIENT_ID="your_google_client_id"
export GOOGLE_CLIENT_SECRET="your_google_client_secret"
```

## Priority Order

The system checks secrets in this order:

1. **Streamlit secrets** (`st.secrets`) - from `.streamlit/secrets.toml` in project
2. **User home secrets** - from `~/.streamlit/secrets.toml`
3. **Environment variables** - from `os.getenv()`

## Verification

After setting up secrets, restart the backend and check the terminal output. You should see:

```
Checking for user secrets at: /Users/charles/.streamlit/secrets.toml
Found user secrets file: /Users/charles/.streamlit/secrets.toml
Loaded X secrets from user home directory
User secrets keys: ['GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_SECRET', ...]
Found GOOGLE_CLIENT_ID: ...
Found GOOGLE_CLIENT_SECRET: ...
```

