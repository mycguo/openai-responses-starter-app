from fastapi import APIRouter, Request, Query
from fastapi.responses import RedirectResponse
import httpx
import time
from lib.session import get_session_id, save_token_set, OAuthTokens
from lib.connectors_auth import get_google_client_config, get_redirect_uri
from lib.config import get_node_env

router = APIRouter()

STATE_COOKIE = "gc_oauth_state"
VERIFIER_COOKIE = "gc_oauth_verifier"


@router.get("")
async def get_google_callback(
    request: Request,
    code: str = Query(None),
    state: str = Query(None),
    error: str = Query(None),
):
    """Handle Google OAuth callback"""
    config = get_google_client_config()
    
    state_cookie = request.cookies.get(STATE_COOKIE)
    verifier = request.cookies.get(VERIFIER_COOKIE)
    session_id = get_session_id(request)
    
    # Clear the one-time cookies regardless of outcome
    redirect_response = RedirectResponse(url="/")
    redirect_response.delete_cookie(STATE_COOKIE, path="/")
    redirect_response.delete_cookie(VERIFIER_COOKIE, path="/")
    
    if not session_id:
        redirect_response.headers["Location"] = "/?error=no-session"
        return redirect_response
    
    if not state_cookie or not verifier or not code or state != state_cookie:
        redirect_response.headers["Location"] = "/?error=invalid_state"
        return redirect_response
    
    try:
        redirect_uri = get_redirect_uri()
        
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                config["token_endpoint"],
                data={
                    "client_id": config["client_id"],
                    "client_secret": config["client_secret"],
                    "code": code,
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code",
                    "code_verifier": verifier,
                },
            )
            token_response.raise_for_status()
            token_data = token_response.json()
        
        now = int(time.time() * 1000)  # milliseconds
        tokens = OAuthTokens(
            access_token=token_data.get("access_token"),
            refresh_token=token_data.get("refresh_token"),
            id_token=token_data.get("id_token"),
            token_type=token_data.get("token_type"),
            scope=token_data.get("scope"),
            expires_at=(
                now + token_data.get("expires_in", 0) * 1000
                if token_data.get("expires_in")
                else None
            ),
        )
        
        # Save tokens in memory
        save_token_set(session_id, tokens)
        
        # Also persist tokens in httpOnly cookies
        cookie_options = {
            "httponly": True,
            "samesite": "lax",
            "path": "/",
            "secure": get_node_env() == "production",
            "max_age": 60 * 60 * 24 * 7,  # 7 days
        }
        
        if tokens.access_token:
            redirect_response.set_cookie("gc_access_token", tokens.access_token, **cookie_options)
        if tokens.refresh_token:
            redirect_response.set_cookie("gc_refresh_token", tokens.refresh_token, **cookie_options)
        if tokens.id_token:
            redirect_response.set_cookie("gc_id_token", tokens.id_token, **cookie_options)
        if tokens.expires_at:
            redirect_response.set_cookie("gc_expires_at", str(tokens.expires_at), **cookie_options)
        
        redirect_response.headers["Location"] = "/?connected=1"
        return redirect_response
    except Exception as e:
        print(f"OAuth callback error: {e}")
        redirect_response.headers["Location"] = "/?error=oauth_failed"
        return redirect_response

