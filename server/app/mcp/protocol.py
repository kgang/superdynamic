"""
MCP (Model Context Protocol) JSON-RPC handler.

Implements the core MCP protocol methods:
- initialize: Server handshake
- tools/list: List available tools
- tools/call: Execute a tool (requires authentication)
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, status, Depends, Header
from app.models import MCPToolCallResponse
from app.mcp.tools import get_available_tools, execute_tool
from app.oauth.token import verify_access_token
from app.config import settings

router = APIRouter()


async def get_current_user(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    """
    Dependency to extract and verify the current user from Bearer token.

    Args:
        authorization: Authorization header with Bearer token

    Returns:
        Decoded token claims with user information

    Raises:
        HTTPException: If token is missing or invalid
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
            headers={
                "WWW-Authenticate": (
                    f'Bearer realm="mcp-server", '
                    f'as_uri="{settings.SERVER_URL}/.well-known/oauth-authorization-server", '
                    f'resource="{settings.SERVER_URL}"'
                )
            }
        )

    # Extract Bearer token
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format. Expected 'Bearer <token>'",
            headers={"WWW-Authenticate": "Bearer"}
        )

    token = parts[1]

    # Verify token
    try:
        claims = verify_access_token(token)
        return claims
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token verification failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"}
        )


@router.post("/mcp/initialize")
async def initialize(request: Dict[str, Any]):
    """
    MCP initialize method.

    This is the handshake between client and server to establish capabilities.
    Unlike tool calls, initialization does not require authentication.

    Request format (JSON-RPC 2.0):
    {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "0.1.0",
            "clientInfo": {...}
        }
    }
    """
    # Validate JSON-RPC format
    if request.get("jsonrpc") != "2.0":
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "error": {
                "code": -32600,
                "message": "Invalid Request: jsonrpc must be '2.0'"
            }
        }

    # Build response
    return {
        "jsonrpc": "2.0",
        "id": request.get("id"),
        "result": {
            "protocolVersion": "0.1.0",
            "serverInfo": {
                "name": settings.MCP_SERVER_NAME,
                "version": settings.MCP_SERVER_VERSION
            },
            "capabilities": {
                "tools": True,
                "authentication": {
                    "oauth2": True,
                    "pkce": True,
                    "dcr": True
                }
            }
        }
    }


@router.post("/mcp/tools/list")
async def list_tools(
    request: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    MCP tools/list method.

    Returns the list of available tools. Requires authentication.

    Request format (JSON-RPC 2.0):
    {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    }
    """
    # Validate JSON-RPC format
    if request.get("jsonrpc") != "2.0":
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "error": {
                "code": -32600,
                "message": "Invalid Request: jsonrpc must be '2.0'"
            }
        }

    # Get available tools
    tools = get_available_tools()

    return {
        "jsonrpc": "2.0",
        "id": request.get("id"),
        "result": {
            "tools": [tool.model_dump() for tool in tools]
        }
    }


@router.post("/mcp/tools/call")
async def call_tool(
    request: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    MCP tools/call method.

    Executes a tool with the given parameters. Requires authentication.

    Request format (JSON-RPC 2.0):
    {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "get_weather",
            "arguments": {
                "location": "San Francisco, CA",
                "units": "fahrenheit"
            }
        }
    }
    """
    # Validate JSON-RPC format
    if request.get("jsonrpc") != "2.0":
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "error": {
                "code": -32600,
                "message": "Invalid Request: jsonrpc must be '2.0'"
            }
        }

    # Extract parameters
    params = request.get("params", {})
    tool_name = params.get("name")
    arguments = params.get("arguments", {})

    if not tool_name:
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "error": {
                "code": -32602,
                "message": "Invalid params: 'name' is required"
            }
        }

    # Get user ID from token
    user_id = current_user.get("sub", "unknown")

    # Execute tool
    try:
        result = execute_tool(tool_name, arguments, user_id)
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "result": result
        }
    except ValueError as e:
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "error": {
                "code": -32601,
                "message": f"Method not found: {str(e)}"
            }
        }
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "error": {
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
        }
