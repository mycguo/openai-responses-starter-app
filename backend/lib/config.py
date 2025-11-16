"""Configuration utility that uses Streamlit secrets"""
import os
from pathlib import Path
from typing import Optional

# Try to import streamlit for secrets access
try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False
    st = None

# Try to load secrets from user home directory if available
def _load_user_secrets():
    """Load secrets from ~/.streamlit/secrets.toml if it exists"""
    try:
        user_secrets_path = Path.home() / ".streamlit" / "secrets.toml"
        print(f"Checking for user secrets at: {user_secrets_path}")
        if user_secrets_path.exists():
            print(f"Found user secrets file: {user_secrets_path}")
            try:
                import tomllib  # Python 3.11+
                with open(user_secrets_path, "rb") as f:
                    secrets = tomllib.load(f)
                    print(f"Loaded {len(secrets)} secrets from user home directory")
                    return secrets
            except ImportError:
                # Fall back to tomli for older Python versions
                try:
                    import tomli
                    with open(user_secrets_path, "rb") as f:
                        secrets = tomli.load(f)
                        print(f"Loaded {len(secrets)} secrets from user home directory (using tomli)")
                        return secrets
                except ImportError:
                    print("Warning: No TOML parser available (tomllib or tomli)")
                    pass
        else:
            print(f"User secrets file not found at: {user_secrets_path}")
    except Exception as e:
        print(f"Error loading user secrets: {e}")
        import traceback
        traceback.print_exc()
    return None

USER_SECRETS = _load_user_secrets()
if USER_SECRETS:
    print(f"User secrets keys: {list(USER_SECRETS.keys())}")


def get_secret(key: str, default: Optional[str] = None) -> Optional[str]:
    """
    Get a secret value from Streamlit secrets (st.secrets).
    Falls back to environment variables if st.secrets is not available.
    
    Priority:
    1. Streamlit secrets (st.secrets[key] or st.secrets.key)
    2. Environment variables
    3. Default value
    
    Args:
        key: The key to look up
        default: Default value if not found
        
    Returns:
        The secret value or default
    """
    # Try Streamlit secrets first (from app's .streamlit/secrets.toml)
    if STREAMLIT_AVAILABLE:
        try:
            # Check if st.secrets exists and is accessible
            if hasattr(st, 'secrets') and st.secrets is not None:
                # Try dictionary access first: st.secrets["key"]
                try:
                    if isinstance(st.secrets, dict) and key in st.secrets:
                        value = st.secrets[key]
                        if value is not None:
                            return str(value)
                except (KeyError, TypeError):
                    pass
                
                # Try attribute access: st.secrets.key
                try:
                    if hasattr(st.secrets, key):
                        value = getattr(st.secrets, key)
                        if value is not None:
                            return str(value)
                except (AttributeError, TypeError):
                    pass
                
                # Try nested access for keys with dots (e.g., "api.openai_key")
                if "." in key:
                    parts = key.split(".")
                    value = st.secrets
                    for part in parts:
                        if isinstance(value, dict) and part in value:
                            value = value[part]
                        elif hasattr(value, part):
                            value = getattr(value, part)
                        else:
                            value = None
                            break
                    if value is not None:
                        return str(value)
        except Exception as e:
            # Log but don't fail - fall back to other sources
            print(f"Warning: Could not access st.secrets for key '{key}': {e}")
    
    # Try user home directory secrets (~/streamlit/secrets.toml)
    if USER_SECRETS:
        try:
            if isinstance(USER_SECRETS, dict) and key in USER_SECRETS:
                value = USER_SECRETS[key]
                if value is not None:
                    print(f"Found {key} in user secrets file")
                    return str(value)
            # Try nested access
            if "." in key:
                parts = key.split(".")
                value = USER_SECRETS
                for part in parts:
                    if isinstance(value, dict) and part in value:
                        value = value[part]
                    else:
                        value = None
                        break
                if value is not None:
                    print(f"Found {key} in user secrets file (nested)")
                    return str(value)
        except Exception as e:
            print(f"Error accessing user secrets for key '{key}': {e}")
    
    # Fall back to environment variables
    return os.getenv(key, default)


# Convenience functions for common secrets
def get_openai_api_key() -> Optional[str]:
    """Get OpenAI API key"""
    return get_secret("OPENAI_API_KEY") or get_secret("openai_api_key")


def get_google_client_id() -> Optional[str]:
    """Get Google OAuth client ID"""
    value = get_secret("GOOGLE_CLIENT_ID") or get_secret("google_client_id")
    if value:
        print(f"Found GOOGLE_CLIENT_ID: {value[:10]}...")
    else:
        print("GOOGLE_CLIENT_ID not found in any source")
    return value


def get_google_client_secret() -> Optional[str]:
    """Get Google OAuth client secret"""
    value = get_secret("GOOGLE_CLIENT_SECRET") or get_secret("google_client_secret")
    if value:
        print(f"Found GOOGLE_CLIENT_SECRET: {value[:10]}...")
    else:
        print("GOOGLE_CLIENT_SECRET not found in any source")
    return value


def get_google_redirect_uri() -> str:
    """Get Google OAuth redirect URI"""
    return get_secret(
        "GOOGLE_REDIRECT_URI",
        "http://localhost:8501/api/google/callback"
    )


def get_node_env() -> str:
    """Get NODE_ENV (development or production)"""
    return get_secret("NODE_ENV", "development")

