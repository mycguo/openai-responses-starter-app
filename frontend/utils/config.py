"""Configuration utility for frontend using Streamlit secrets"""
import streamlit as st
import os
from pathlib import Path
from typing import Optional

# Try to load secrets from user home directory if available
def _load_user_secrets():
    """Load secrets from ~/.streamlit/secrets.toml if it exists"""
    try:
        user_secrets_path = Path.home() / ".streamlit" / "secrets.toml"
        if user_secrets_path.exists():
            import tomllib  # Python 3.11+
            with open(user_secrets_path, "rb") as f:
                return tomllib.load(f)
    except ImportError:
        # Fall back to tomli for older Python versions
        try:
            import tomli
            user_secrets_path = Path.home() / ".streamlit" / "secrets.toml"
            if user_secrets_path.exists():
                with open(user_secrets_path, "rb") as f:
                    return tomli.load(f)
        except ImportError:
            pass
    except Exception:
        pass
    return None

USER_SECRETS = _load_user_secrets()


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
    try:
        # Try Streamlit secrets first (from app's .streamlit/secrets.toml)
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
            
            # Try nested access for keys with dots (e.g., "api.base_url")
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
    except Exception:
        pass
    
    # Try user home directory secrets (~/streamlit/secrets.toml)
    if USER_SECRETS:
        try:
            if isinstance(USER_SECRETS, dict) and key in USER_SECRETS:
                value = USER_SECRETS[key]
                if value is not None:
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
                    return str(value)
        except Exception:
            pass
    
    # Fall back to environment variables
    return os.getenv(key, default)


def get_api_base_url() -> str:
    """Get API base URL from secrets or environment"""
    return get_secret("API_BASE_URL", "http://localhost:8000")

