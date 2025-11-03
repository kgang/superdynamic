"""
OAuth 2.0 Authorization Endpoint with PKCE support.
"""

import secrets
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, status, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from app.models import (
    AuthorizationCode,
    CodeChallengeMethod
)
from app.storage import storage
from app.config import settings

router = APIRouter()


def generate_authorization_code() -> str:
    """Generate a secure authorization code."""
    return secrets.token_urlsafe(32)


@router.get("/oauth/authorize")
async def authorize(
    response_type: str,
    client_id: str,
    redirect_uri: str,
    code_challenge: str,
    code_challenge_method: str = "S256",
    scope: str = None,
    state: str = None,
):
    """
    OAuth 2.0 Authorization Endpoint with PKCE.

    This endpoint initiates the authorization code flow. In a real implementation,
    this would present a consent screen to the user. For this mock server,
    we auto-approve the request.

    Query Parameters:
        response_type: Must be "code"
        client_id: Registered client identifier
        redirect_uri: Client's callback URI
        code_challenge: PKCE code challenge
        code_challenge_method: PKCE method (S256 or plain)
        scope: Requested scopes (optional)
        state: Client state for CSRF protection (optional)

    Returns:
        Redirect to client's redirect_uri with authorization code
    """
    # Validate response type
    if response_type != "code":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported response_type. Only 'code' is supported."
        )

    # Validate client
    client = storage.get_client(client_id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid client_id"
        )

    # Validate redirect URI
    if redirect_uri not in client.redirect_uris:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid redirect_uri"
        )

    # Validate PKCE parameters
    if not code_challenge:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="code_challenge is required"
        )

    try:
        challenge_method = CodeChallengeMethod(code_challenge_method)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported code_challenge_method: {code_challenge_method}"
        )

    # Generate authorization code
    code = generate_authorization_code()

    # Store authorization code
    auth_code = AuthorizationCode(
        code=code,
        client_id=client_id,
        redirect_uri=redirect_uri,
        scope=scope or client.scope,
        code_challenge=code_challenge,
        code_challenge_method=challenge_method,
        user_id="mock_user_123",  # Mock user ID
        expires_at=datetime.utcnow() + timedelta(
            minutes=settings.OAUTH_AUTHORIZATION_CODE_EXPIRE_MINUTES
        ),
        used=False
    )
    storage.store_authorization_code(auth_code)

    # Build redirect URL
    redirect_url = f"{redirect_uri}?code={code}"
    if state:
        redirect_url += f"&state={state}"

    return RedirectResponse(url=redirect_url)


@router.get("/oauth/consent")
async def consent_page(
    client_id: str,
    scope: str = None,
    state: str = None,
):
    """
    Simple consent page for demonstration.

    In production, this would be a proper HTML page with user consent flow.
    For this mock, we provide a minimal HTML page that auto-approves.
    """
    client = storage.get_client(client_id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid client_id"
        )

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Authorization Request</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 600px;
                margin: 50px auto;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            .container {{
                background-color: white;
                padding: 30px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            h1 {{ color: #333; }}
            .info {{ margin: 20px 0; }}
            .scope {{
                background-color: #e3f2fd;
                padding: 10px;
                border-radius: 4px;
                margin: 10px 0;
            }}
            button {{
                background-color: #4CAF50;
                color: white;
                padding: 12px 24px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 16px;
            }}
            button:hover {{
                background-color: #45a049;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Authorization Request</h1>
            <div class="info">
                <p><strong>Application:</strong> {client.client_name or client_id}</p>
                <p><strong>Requested Scopes:</strong></p>
                <div class="scope">{scope or client.scope or "Default scopes"}</div>
            </div>
            <p>This application is requesting access to your MCP resources.</p>
            <p><em>Note: This is a mock server - authorization is automatically approved.</em></p>
            <button onclick="window.close()">Approve</button>
        </div>
    </body>
    </html>
    """

    return HTMLResponse(content=html_content)
