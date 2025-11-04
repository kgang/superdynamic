"""
OAuth 2.0 Token Endpoint with PKCE validation and refresh token support.
"""

import secrets
from datetime import datetime, timedelta
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, status, Form
from jose import jwt, JWTError
from app.models import (
    TokenResponse,
    RefreshToken,
    GrantType
)
from app.storage import storage
from app.config import settings
from app.oauth.pkce import verify_code_challenge

router = APIRouter()


def generate_refresh_token() -> str:
    """Generate a secure refresh token."""
    return secrets.token_urlsafe(32)


def create_access_token(
    client_id: str,
    user_id: str,
    scope: str = None
) -> tuple[str, int]:
    """
    Create a JWT access token.

    Args:
        client_id: Client identifier
        user_id: User identifier
        scope: Granted scopes

    Returns:
        Tuple of (token, expires_in_seconds)
    """
    expires_in = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
    expires_at = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)

    claims = {
        "sub": user_id,
        "client_id": client_id,
        "scope": scope or "",
        "exp": expires_at,
        "iat": datetime.utcnow(),
        "iss": settings.SERVER_URL,
        "aud": settings.SERVER_URL
    }

    token = jwt.encode(
        claims,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

    return token, expires_in


def verify_access_token(token: str) -> Dict[str, Any]:
    """
    Verify and decode a JWT access token.

    Args:
        token: JWT access token

    Returns:
        Decoded token claims

    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            audience=settings.SERVER_URL
        )
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"}
        )


@router.post("/oauth/token", response_model=TokenResponse)
async def token_endpoint(
    grant_type: str = Form(...),
    code: str = Form(None),
    redirect_uri: str = Form(None),
    code_verifier: str = Form(None),
    refresh_token: str = Form(None),
    client_id: str = Form(...),
    client_secret: str = Form(None),
):
    """
    OAuth 2.0 Token Endpoint.

    Supports two grant types:
    1. authorization_code - Exchange authorization code for tokens (with PKCE)
    2. refresh_token - Refresh an access token

    Form Parameters:
        grant_type: Type of grant (authorization_code or refresh_token)
        code: Authorization code (for authorization_code grant)
        redirect_uri: Client's redirect URI (for authorization_code grant)
        code_verifier: PKCE code verifier (for authorization_code grant)
        refresh_token: Refresh token (for refresh_token grant)
        client_id: Client identifier
        client_secret: Client secret (optional for public clients)

    Returns:
        Access token, refresh token, and metadata
    """
    # Validate client
    client = storage.get_client(client_id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid client credentials"
        )

    # Verify client secret if provided by the request
    # Note: For PKCE flows (public clients), client_secret is optional
    # The code_verifier serves as proof of client identity
    if client_secret is not None:
        # If client_secret was provided in request, it must match
        if client.client_secret != client_secret:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid client credentials"
            )

    # Handle authorization_code grant
    if grant_type == GrantType.AUTHORIZATION_CODE.value:
        if not code or not redirect_uri or not code_verifier:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="code, redirect_uri, and code_verifier are required"
            )

        # Retrieve authorization code
        auth_code = storage.get_authorization_code(code)
        if not auth_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired authorization code"
            )

        # Validate client ID
        if auth_code.client_id != client_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Authorization code was issued to different client"
            )

        # Validate redirect URI
        if auth_code.redirect_uri != redirect_uri:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Redirect URI mismatch"
            )

        # Verify PKCE code verifier
        if not verify_code_challenge(
            code_verifier,
            auth_code.code_challenge,
            auth_code.code_challenge_method
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid code_verifier"
            )

        # Atomically mark code as used (prevents race conditions)
        if not storage.mark_code_as_used(code):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Authorization code already used or expired"
            )

        # Generate tokens
        access_token, expires_in = create_access_token(
            client_id=client_id,
            user_id=auth_code.user_id,
            scope=auth_code.scope
        )

        refresh_token_value = generate_refresh_token()

        # Store refresh token
        refresh_token_obj = RefreshToken(
            token=refresh_token_value,
            client_id=client_id,
            user_id=auth_code.user_id,
            scope=auth_code.scope,
            expires_at=datetime.utcnow() + timedelta(
                days=settings.OAUTH_REFRESH_TOKEN_EXPIRE_DAYS
            ),
            revoked=False
        )
        storage.store_refresh_token(refresh_token_obj)

        return TokenResponse(
            access_token=access_token,
            token_type="Bearer",
            expires_in=expires_in,
            refresh_token=refresh_token_value,
            scope=auth_code.scope
        )

    # Handle refresh_token grant
    elif grant_type == GrantType.REFRESH_TOKEN.value:
        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="refresh_token is required"
            )

        # Retrieve refresh token
        refresh_token_obj = storage.get_refresh_token(refresh_token)
        if not refresh_token_obj:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired refresh token"
            )

        # Validate client ID
        if refresh_token_obj.client_id != client_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Refresh token was issued to different client"
            )

        # Generate new access token
        access_token, expires_in = create_access_token(
            client_id=client_id,
            user_id=refresh_token_obj.user_id,
            scope=refresh_token_obj.scope
        )

        return TokenResponse(
            access_token=access_token,
            token_type="Bearer",
            expires_in=expires_in,
            refresh_token=refresh_token,  # Return same refresh token
            scope=refresh_token_obj.scope
        )

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported grant_type: {grant_type}"
        )
