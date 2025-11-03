"""
Pydantic models for OAuth, DCR, and MCP protocol.
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ============================================================================
# OAuth Models
# ============================================================================

class GrantType(str, Enum):
    """OAuth grant types."""
    AUTHORIZATION_CODE = "authorization_code"
    REFRESH_TOKEN = "refresh_token"


class ResponseType(str, Enum):
    """OAuth response types."""
    CODE = "code"


class TokenType(str, Enum):
    """OAuth token types."""
    BEARER = "Bearer"


class CodeChallengeMethod(str, Enum):
    """PKCE code challenge methods."""
    S256 = "S256"
    PLAIN = "plain"


# ============================================================================
# Dynamic Client Registration (RFC 7591)
# ============================================================================

class ClientRegistrationRequest(BaseModel):
    """Client registration request per RFC 7591."""
    redirect_uris: List[str] = Field(..., description="Array of redirection URIs")
    client_name: Optional[str] = Field(None, description="Human-readable client name")
    client_uri: Optional[HttpUrl] = Field(None, description="URL of client home page")
    logo_uri: Optional[HttpUrl] = Field(None, description="URL of client logo")
    scope: Optional[str] = Field(None, description="Space-separated list of scopes")
    grant_types: Optional[List[GrantType]] = Field(
        default=["authorization_code", "refresh_token"],
        description="OAuth grant types"
    )
    response_types: Optional[List[ResponseType]] = Field(
        default=["code"],
        description="OAuth response types"
    )


class ClientRegistrationResponse(BaseModel):
    """Client registration response per RFC 7591."""
    client_id: str = Field(..., description="Unique client identifier")
    client_secret: Optional[str] = Field(None, description="Client secret")
    client_secret_expires_at: int = Field(
        0,
        description="Time at which secret expires (0 = never)"
    )
    redirect_uris: List[str]
    client_name: Optional[str] = None
    client_uri: Optional[str] = None
    logo_uri: Optional[str] = None
    scope: Optional[str] = None
    grant_types: List[str]
    response_types: List[str]
    registration_client_uri: Optional[str] = Field(
        None,
        description="URI for client configuration endpoint"
    )
    registration_access_token: Optional[str] = Field(
        None,
        description="Token for accessing client configuration"
    )


# ============================================================================
# Authorization & Token Models
# ============================================================================

class AuthorizationRequest(BaseModel):
    """OAuth authorization request."""
    response_type: str
    client_id: str
    redirect_uri: str
    scope: Optional[str] = None
    state: Optional[str] = None
    code_challenge: str
    code_challenge_method: CodeChallengeMethod = CodeChallengeMethod.S256


class TokenRequest(BaseModel):
    """OAuth token request."""
    grant_type: GrantType
    code: Optional[str] = None  # For authorization_code grant
    redirect_uri: Optional[str] = None  # For authorization_code grant
    code_verifier: Optional[str] = None  # For PKCE
    refresh_token: Optional[str] = None  # For refresh_token grant
    client_id: str
    client_secret: Optional[str] = None


class TokenResponse(BaseModel):
    """OAuth token response."""
    access_token: str
    token_type: str = "Bearer"
    expires_in: int
    refresh_token: Optional[str] = None
    scope: Optional[str] = None


# ============================================================================
# Metadata Models (RFC 8414 & RFC 9728)
# ============================================================================

class AuthorizationServerMetadata(BaseModel):
    """OAuth Authorization Server Metadata per RFC 8414."""
    issuer: str
    authorization_endpoint: str
    token_endpoint: str
    registration_endpoint: str
    response_types_supported: List[str]
    grant_types_supported: List[str]
    code_challenge_methods_supported: List[str]
    token_endpoint_auth_methods_supported: List[str]
    scopes_supported: Optional[List[str]] = None


class ProtectedResourceMetadata(BaseModel):
    """OAuth Protected Resource Metadata per RFC 9728."""
    resource: str
    authorization_servers: List[str]
    scopes_supported: List[str]
    bearer_methods_supported: List[str] = ["header"]


# ============================================================================
# MCP Protocol Models
# ============================================================================

class MCPToolParameter(BaseModel):
    """MCP tool input parameter."""
    type: str
    description: Optional[str] = None
    enum: Optional[List[str]] = None


class MCPToolInputSchema(BaseModel):
    """MCP tool input schema (JSON Schema)."""
    type: str = "object"
    properties: Dict[str, MCPToolParameter]
    required: Optional[List[str]] = None


class MCPTool(BaseModel):
    """MCP tool definition."""
    name: str
    description: str
    inputSchema: MCPToolInputSchema


class MCPToolCallRequest(BaseModel):
    """MCP tool call request."""
    jsonrpc: str = "2.0"
    id: Any
    method: str = "tools/call"
    params: Dict[str, Any]


class MCPToolCallResponse(BaseModel):
    """MCP tool call response."""
    jsonrpc: str = "2.0"
    id: Any
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None


class MCPInitializeRequest(BaseModel):
    """MCP initialize request."""
    jsonrpc: str = "2.0"
    id: Any
    method: str = "initialize"
    params: Dict[str, Any]


class MCPListToolsRequest(BaseModel):
    """MCP list tools request."""
    jsonrpc: str = "2.0"
    id: Any
    method: str = "tools/list"
    params: Optional[Dict[str, Any]] = None


# ============================================================================
# Internal Storage Models
# ============================================================================

class RegisteredClient(BaseModel):
    """Internal model for registered client."""
    client_id: str
    client_secret: Optional[str]
    redirect_uris: List[str]
    client_name: Optional[str]
    client_uri: Optional[str]
    scope: Optional[str]
    grant_types: List[str]
    response_types: List[str]
    created_at: datetime


class AuthorizationCode(BaseModel):
    """Internal model for authorization code."""
    code: str
    client_id: str
    redirect_uri: str
    scope: Optional[str]
    code_challenge: str
    code_challenge_method: CodeChallengeMethod
    user_id: str  # Mock user
    expires_at: datetime
    used: bool = False


class RefreshToken(BaseModel):
    """Internal model for refresh token."""
    token: str
    client_id: str
    user_id: str
    scope: Optional[str]
    expires_at: datetime
    revoked: bool = False
