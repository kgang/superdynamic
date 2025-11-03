"""
Dynamic Client Registration (RFC 7591) implementation.
"""

import uuid
import secrets
from datetime import datetime
from fastapi import APIRouter, HTTPException, status
from app.models import (
    ClientRegistrationRequest,
    ClientRegistrationResponse,
    RegisteredClient
)
from app.storage import storage
from app.config import settings

router = APIRouter()


def generate_client_id() -> str:
    """Generate a unique client ID."""
    return f"client_{uuid.uuid4().hex}"


def generate_client_secret() -> str:
    """Generate a secure client secret."""
    return secrets.token_urlsafe(32)


@router.post("/oauth/register", response_model=ClientRegistrationResponse)
async def register_client(request: ClientRegistrationRequest):
    """
    Dynamic Client Registration endpoint (RFC 7591).

    Allows clients to self-register without pre-configuration.
    This is critical for the MCP use case where clients need to
    dynamically connect to servers.

    Args:
        request: Client registration request with metadata

    Returns:
        Client credentials and metadata
    """
    # Validate redirect URIs (required for authorization code flow)
    if not request.redirect_uris or len(request.redirect_uris) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="redirect_uris is required and must not be empty"
        )

    # Generate client credentials
    client_id = generate_client_id()
    client_secret = generate_client_secret()

    # Create registered client
    client = RegisteredClient(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uris=request.redirect_uris,
        client_name=request.client_name,
        client_uri=str(request.client_uri) if request.client_uri else None,
        scope=request.scope or "mcp:tools:read mcp:tools:execute",
        grant_types=request.grant_types or ["authorization_code", "refresh_token"],
        response_types=request.response_types or ["code"],
        created_at=datetime.utcnow()
    )

    # Store client
    storage.store_client(client)

    # Build response
    response = ClientRegistrationResponse(
        client_id=client_id,
        client_secret=client_secret,
        client_secret_expires_at=0,  # Never expires in this mock
        redirect_uris=client.redirect_uris,
        client_name=client.client_name,
        client_uri=client.client_uri,
        scope=client.scope,
        grant_types=client.grant_types,
        response_types=client.response_types,
        # Optional: could implement client configuration endpoint
        registration_client_uri=None,
        registration_access_token=None
    )

    return response
