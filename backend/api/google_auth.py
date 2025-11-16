from fastapi import APIRouter, Request, Response
from fastapi.responses import RedirectResponse
import secrets
import hashlib
import base64
from urllib.parse import urlencode
from lib.session import get_or_create_session_id
from lib.connectors_auth import get_google_client_config, get_redirect_uri, GOOGLE_SCOPES
from lib.config import get_node_env

router = APIRouter()

STATE_COOKIE = "gc_oauth_state"
VERIFIER_COOKIE = "gc_oauth_verifier"


def generate_code_verifier() -> str:
    """Generate PKCE code verifier"""
    return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode("utf-8").rstrip("=")


def generate_code_challenge(verifier: str) -> str:
    """Generate PKCE code challenge"""
    challenge = hashlib.sha256(verifier.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(challenge).decode("utf-8").rstrip("=")


def generate_state() -> str:
    """Generate OAuth state"""
    return secrets.token_urlsafe(32)


@router.get("")
async def get_google_auth(request: Request, response: Response):
    """Initiate Google OAuth flow"""
    config = get_google_client_config()
    
    # Ensure we have a session id cookie set
    session_id = get_or_create_session_id(request)
    
    state = generate_state()
    code_verifier = generate_code_verifier()
    code_challenge = generate_code_challenge(code_verifier)
    
    # Store state and verifier in httpOnly cookies
    redirect_response = RedirectResponse(url="")
    redirect_response.set_cookie(
        STATE_COOKIE,
        state,
        httponly=True,
        samesite="lax",
        path="/",
        secure=get_node_env() == "production",
        max_age=10 * 60,  # 10 minutes
    )
    redirect_response.set_cookie(
        VERIFIER_COOKIE,
        code_verifier,
        httponly=True,
        samesite="lax",
        path="/",
        secure=get_node_env() == "production",
        max_age=10 * 60,  # 10 minutes
    )
    redirect_response.set_cookie(
        "responses_starter_session_id",
        session_id,
        httponly=True,
        samesite="lax",
        path="/",
        secure=get_node_env() == "production",
    )
    
    redirect_uri = get_redirect_uri()
    
    auth_params = {
        "client_id": config["client_id"],
        "redirect_uri": redirect_uri,
        "scope": " ".join(GOOGLE_SCOPES),
        "response_type": "code",
        "access_type": "offline",
        "include_granted_scopes": "true",
        "prompt": "consent",
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
        "state": state,
    }
    
    authorization_url = f"{config['authorization_endpoint']}?{urlencode(auth_params)}"
    
    redirect_response.headers["Location"] = authorization_url
    redirect_response.status_code = 302
    return redirect_response

