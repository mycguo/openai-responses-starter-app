"""Configuration utility that supports Streamlit secrets and environment variables"""
import os
from typing import Optional

# Try to import streamlit for secrets access
try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False
    st = None


def get_secret(key: str, default: Optional[str] = None) -> Optional[str]:
    """
    Get a secret value from Streamlit secrets or environment variables.
    
    Priority:
    1. Streamlit secrets (if available)
    2. Environment variables
    3. Default value
    
    Args:
        key: The key to look up
        default: Default value if not found
        
    Returns:
        The secret value or default
    """
    # Try Streamlit secrets first
    if STREAMLIT_AVAILABLE:
        try:
            # Access secrets using dot notation (e.g., "OPENAI_API_KEY")
            # Streamlit secrets are accessed via st.secrets["key"] or st.secrets.key
            if hasattr(st, 'secrets') and st.secrets is not None:
                # Try different access patterns
                if key in st.secrets:
                    return st.secrets[key]
                elif hasattr(st.secrets, key):
                    return getattr(st.secrets, key)
                # Try nested access (e.g., st.secrets["api"]["openai_key"])
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
        except (AttributeError, KeyError, TypeError):
            pass
    
    # Fall back to environment variables
    return os.getenv(key, default)


# Convenience functions for common secrets
def get_openai_api_key() -> Optional[str]:
    """Get OpenAI API key"""
    return get_secret("OPENAI_API_KEY") or get_secret("openai_api_key")


def get_google_client_id() -> Optional[str]:
    """Get Google OAuth client ID"""
    return get_secret("GOOGLE_CLIENT_ID") or get_secret("google_client_id")


def get_google_client_secret() -> Optional[str]:
    """Get Google OAuth client secret"""
    return get_secret("GOOGLE_CLIENT_SECRET") or get_secret("google_client_secret")


def get_google_redirect_uri() -> str:
    """Get Google OAuth redirect URI"""
    return get_secret(
        "GOOGLE_REDIRECT_URI",
        "http://localhost:8501/api/google/callback"
    )


def get_node_env() -> str:
    """Get NODE_ENV (development or production)"""
    return get_secret("NODE_ENV", "development")

