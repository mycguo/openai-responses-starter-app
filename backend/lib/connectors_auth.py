from typing import Optional, Dict
import httpx
from lib.session import get_token_set, save_token_set, get_session_id
from lib.config import get_google_client_id, get_google_client_secret, get_google_redirect_uri

GOOGLE_SCOPES = [
    "openid",
    "email",
    "profile",
    "https://www.googleapis.com/auth/calendar.events.readonly",
    "https://www.googleapis.com/auth/gmail.readonly",
]


class FreshTokens:
    accessToken: Optional[str] = None
    refreshToken: Optional[str] = None
    expiresAt: Optional[int] = None


def get_google_client_config() -> Dict[str, str]:
    """Get Google OAuth client configuration"""
    client_id = get_google_client_id()
    client_secret = get_google_client_secret()
    
    if not client_id or not client_secret:
        raise ValueError(
            "Missing GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET environment variables"
        )
    
    return {
        "client_id": client_id,
        "client_secret": client_secret,
        "authorization_endpoint": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_endpoint": "https://oauth2.googleapis.com/token",
    }


def get_redirect_uri() -> str:
    """Get Google OAuth redirect URI"""
    return get_google_redirect_uri()


# Refresh when close to expiry (30s) or when missing access token but we have a refresh token
EXPIRY_SKEW_MS = 30_000


async def get_fresh_access_token(request) -> FreshTokens:
    """Get fresh access token, refreshing if needed"""
    session_id = get_session_id(request)
    token_set = get_token_set(session_id)
    
    access_token = request.cookies.get("gc_access_token") or (token_set.access_token if token_set else None)
    refresh_token = request.cookies.get("gc_refresh_token") or (token_set.refresh_token if token_set else None)
    expires_at_str = request.cookies.get("gc_expires_at")
    expires_at = int(expires_at_str) if expires_at_str else (token_set.expires_at if token_set else None)
    
    import time
    now = int(time.time() * 1000)  # milliseconds
    is_expiring_soon = expires_at is not None and now > expires_at - EXPIRY_SKEW_MS
    should_refresh = bool(refresh_token and (not access_token or is_expiring_soon))
    
    if should_refresh:
        try:
            config = get_google_client_config()
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    config["token_endpoint"],
                    data={
                        "client_id": config["client_id"],
                        "client_secret": config["client_secret"],
                        "refresh_token": refresh_token,
                        "grant_type": "refresh_token",
                    },
                )
                response.raise_for_status()
                refreshed = response.json()
                
                access_token = refreshed.get("access_token") or access_token
                refresh_token = refreshed.get("refresh_token") or refresh_token
                expires_at = (
                    now + refreshed.get("expires_in", 0) * 1000
                    if refreshed.get("expires_in")
                    else expires_at
                )
                
                # Note: In FastAPI, we'd need to set cookies in the response
                # This is handled in the callback endpoint
                if session_id and token_set:
                    from lib.session import OAuthTokens
                    save_token_set(
                        session_id,
                        OAuthTokens(
                            access_token=access_token,
                            refresh_token=refresh_token,
                            expires_at=expires_at,
                        ),
                    )
        except Exception:
            # If refresh fails, fall through and return whatever we have
            pass
    
    tokens = FreshTokens()
    tokens.accessToken = access_token
    tokens.refreshToken = refresh_token
    tokens.expiresAt = expires_at
    return tokens

