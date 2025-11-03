"""
OAuth Authorization Server Metadata (RFC 8414) and
OAuth Protected Resource Metadata (RFC 9728) endpoints.
"""

from fastapi import APIRouter
from app.models import AuthorizationServerMetadata, ProtectedResourceMetadata
from app.config import settings

router = APIRouter()


@router.get("/.well-known/oauth-authorization-server")
async def authorization_server_metadata() -> AuthorizationServerMetadata:
    """
    OAuth 2.0 Authorization Server Metadata endpoint (RFC 8414).

    Provides server capabilities and endpoint locations for client discovery.
    """
    return AuthorizationServerMetadata(
        issuer=settings.SERVER_URL,
        authorization_endpoint=f"{settings.SERVER_URL}/oauth/authorize",
        token_endpoint=f"{settings.SERVER_URL}/oauth/token",
        registration_endpoint=f"{settings.SERVER_URL}/oauth/register",
        response_types_supported=["code"],
        grant_types_supported=["authorization_code", "refresh_token"],
        code_challenge_methods_supported=["S256"],
        token_endpoint_auth_methods_supported=["none", "client_secret_post"],
        scopes_supported=["mcp:tools:read", "mcp:tools:execute"],
    )


@router.get("/.well-known/oauth-protected-resource")
async def protected_resource_metadata() -> ProtectedResourceMetadata:
    """
    OAuth 2.0 Protected Resource Metadata endpoint (RFC 9728).

    Indicates the location of authorization servers and supported scopes.
    This is critical for MCP clients to discover how to authenticate.
    """
    return ProtectedResourceMetadata(
        resource=settings.SERVER_URL,
        authorization_servers=[settings.SERVER_URL],
        scopes_supported=["mcp:tools:read", "mcp:tools:execute"],
        bearer_methods_supported=["header"],
    )
