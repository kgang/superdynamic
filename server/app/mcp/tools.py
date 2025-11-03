"""
Example MCP tools for demonstration.

These tools require OAuth authentication to access.
"""

from typing import Dict, Any
from app.models import MCPTool, MCPToolInputSchema, MCPToolParameter


# ============================================================================
# Tool Definitions
# ============================================================================

AVAILABLE_TOOLS = [
    MCPTool(
        name="get_weather",
        description="Get current weather information for a specified location",
        inputSchema=MCPToolInputSchema(
            type="object",
            properties={
                "location": MCPToolParameter(
                    type="string",
                    description="City name or location (e.g., 'San Francisco, CA')"
                ),
                "units": MCPToolParameter(
                    type="string",
                    description="Temperature units (celsius or fahrenheit)",
                    enum=["celsius", "fahrenheit"]
                )
            },
            required=["location"]
        )
    ),
    MCPTool(
        name="list_files",
        description="List files in a simulated directory structure",
        inputSchema=MCPToolInputSchema(
            type="object",
            properties={
                "path": MCPToolParameter(
                    type="string",
                    description="Directory path to list (e.g., '/home/user')"
                ),
                "pattern": MCPToolParameter(
                    type="string",
                    description="Optional glob pattern to filter files (e.g., '*.txt')"
                )
            },
            required=["path"]
        )
    ),
    MCPTool(
        name="get_user_profile",
        description="Get the authenticated user's profile information",
        inputSchema=MCPToolInputSchema(
            type="object",
            properties={},
            required=[]
        )
    ),
]


# ============================================================================
# Tool Implementations
# ============================================================================

def execute_get_weather(params: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    """
    Execute the get_weather tool.

    Returns mock weather data for the requested location.
    """
    location = params.get("location")
    units = params.get("units", "fahrenheit")

    # Mock weather data
    mock_weather = {
        "location": location,
        "temperature": 72 if units == "fahrenheit" else 22,
        "units": units,
        "conditions": "Partly Cloudy",
        "humidity": "65%",
        "wind_speed": "10 mph",
        "forecast": [
            {"day": "Today", "high": 75, "low": 58, "conditions": "Partly Cloudy"},
            {"day": "Tomorrow", "high": 78, "low": 61, "conditions": "Sunny"},
            {"day": "Wednesday", "high": 73, "low": 59, "conditions": "Cloudy"},
        ]
    }

    return {
        "success": True,
        "data": mock_weather,
        "message": f"Weather data for {location}"
    }


def execute_list_files(params: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    """
    Execute the list_files tool.

    Returns mock file listing data.
    """
    path = params.get("path")
    pattern = params.get("pattern", "*")

    # Mock file data
    mock_files = [
        {"name": "document.txt", "size": 1024, "type": "file", "modified": "2025-11-01T10:30:00Z"},
        {"name": "reports", "size": 4096, "type": "directory", "modified": "2025-11-02T14:15:00Z"},
        {"name": "image.png", "size": 524288, "type": "file", "modified": "2025-11-03T09:00:00Z"},
        {"name": "data.json", "size": 2048, "type": "file", "modified": "2025-10-30T16:45:00Z"},
        {"name": "scripts", "size": 4096, "type": "directory", "modified": "2025-10-28T11:20:00Z"},
    ]

    # Simple pattern filtering
    if pattern != "*":
        filtered_files = [
            f for f in mock_files
            if pattern.replace("*", "") in f["name"]
        ]
    else:
        filtered_files = mock_files

    return {
        "success": True,
        "data": {
            "path": path,
            "pattern": pattern,
            "files": filtered_files,
            "total": len(filtered_files)
        },
        "message": f"Listed {len(filtered_files)} items in {path}"
    }


def execute_get_user_profile(params: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    """
    Execute the get_user_profile tool.

    Returns user profile information based on the authenticated user.
    """
    # Mock user profile data
    mock_profile = {
        "user_id": user_id,
        "username": f"user_{user_id}",
        "email": f"{user_id}@example.com",
        "full_name": "Mock User",
        "created_at": "2025-01-01T00:00:00Z",
        "roles": ["user", "developer"],
        "preferences": {
            "theme": "dark",
            "language": "en",
            "timezone": "America/Los_Angeles"
        }
    }

    return {
        "success": True,
        "data": mock_profile,
        "message": "User profile retrieved successfully"
    }


# ============================================================================
# Tool Execution Router
# ============================================================================

TOOL_EXECUTORS = {
    "get_weather": execute_get_weather,
    "list_files": execute_list_files,
    "get_user_profile": execute_get_user_profile,
}


def execute_tool(tool_name: str, params: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    """
    Execute a tool by name with the given parameters.

    Args:
        tool_name: Name of the tool to execute
        params: Tool parameters
        user_id: Authenticated user ID

    Returns:
        Tool execution result

    Raises:
        ValueError: If tool not found
    """
    if tool_name not in TOOL_EXECUTORS:
        raise ValueError(f"Unknown tool: {tool_name}")

    executor = TOOL_EXECUTORS[tool_name]
    return executor(params, user_id)


def get_available_tools() -> list[MCPTool]:
    """Get list of available MCP tools."""
    return AVAILABLE_TOOLS
