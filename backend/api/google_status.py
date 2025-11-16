from fastapi import APIRouter, Request
from lib.session import get_session_id, get_token_set
from lib.config import get_google_client_id, get_google_client_secret

router = APIRouter()


@router.get("")
async def get_google_status(request: Request):
    """Get Google OAuth connection status"""
    session_id = get_session_id(request)
    token_set = get_token_set(session_id)
    access_token = request.cookies.get("gc_access_token")
    
    client_id = get_google_client_id()
    client_secret = get_google_client_secret()
    oauth_configured = bool(client_id and client_secret)
    
    print(f"Google OAuth Status Check:")
    print(f"  client_id present: {bool(client_id)}")
    print(f"  client_secret present: {bool(client_secret)}")
    print(f"  oauth_configured: {oauth_configured}")
    
    return {
        "connected": bool(token_set or access_token),
        "oauthConfigured": oauth_configured,
    }

