from typing import Optional, Dict
import secrets
from datetime import datetime, timedelta

# Simple in-memory storage for demo purposes only.
# In production, replace with a persistent/session store (Redis, database, etc.)
session_store: Dict[str, "OAuthTokens"] = {}


class OAuthTokens:
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    id_token: Optional[str] = None
    token_type: Optional[str] = None
    scope: Optional[str] = None
    expires_at: Optional[int] = None  # epoch milliseconds when the access token expires

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_dict(self) -> dict:
        return {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "id_token": self.id_token,
            "token_type": self.token_type,
            "scope": self.scope,
            "expires_at": self.expires_at,
        }


def get_or_create_session_id(request) -> str:
    """Get or create session ID from cookies"""
    session_id = request.cookies.get("responses_starter_session_id")
    if session_id:
        return session_id
    
    session_id = secrets.token_hex(16)
    return session_id


def get_session_id(request) -> Optional[str]:
    """Get session ID from cookies"""
    return request.cookies.get("responses_starter_session_id")


def save_token_set(session_id: str, token_set: OAuthTokens):
    """Save OAuth tokens for a session"""
    session_store[session_id] = token_set


def get_token_set(session_id: Optional[str]) -> Optional[OAuthTokens]:
    """Get OAuth tokens for a session"""
    if not session_id:
        return None
    return session_store.get(session_id)


def clear_session(session_id: Optional[str]):
    """Clear session data"""
    if session_id:
        session_store.pop(session_id, None)

