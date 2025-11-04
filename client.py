#!/usr/bin/env python3
"""
MCP OAuth DCR Client - Dynamic Client Registration and OAuth 2.0 Flow

This client demonstrates:
1. Dynamic Client Registration (RFC 7591)
2. OAuth 2.0 Authorization Code Flow with PKCE (RFC 7636)
3. Authenticated MCP tool invocation
4. Multi-client lifecycle management
"""

import argparse
import base64
import hashlib
import json
import secrets
import sys
import time
import webbrowser
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Dict, Optional, Any
from urllib.parse import parse_qs, urlencode, urlparse

try:
    import httpx
except ImportError:
    print("Error: httpx is required. Install with: pip install httpx")
    sys.exit(1)


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """HTTP handler for OAuth callback."""

    # Class variable to store authorization code
    authorization_code: Optional[str] = None
    state: Optional[str] = None
    error: Optional[str] = None

    def do_GET(self):
        """Handle OAuth callback GET request."""
        # Parse query parameters
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)

        # Extract authorization code or error
        if "code" in query_params:
            OAuthCallbackHandler.authorization_code = query_params["code"][0]
            OAuthCallbackHandler.state = query_params.get("state", [None])[0]

            # Send success response
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"""
                <html>
                <head><title>Authorization Successful</title></head>
                <body>
                    <h1>Authorization Successful!</h1>
                    <p>You can close this window and return to the terminal.</p>
                </body>
                </html>
            """)
        elif "error" in query_params:
            OAuthCallbackHandler.error = query_params["error"][0]
            error_description = query_params.get("error_description", ["Unknown error"])[0]

            # Send error response
            self.send_response(400)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(f"""
                <html>
                <head><title>Authorization Failed</title></head>
                <body>
                    <h1>Authorization Failed</h1>
                    <p>Error: {OAuthCallbackHandler.error}</p>
                    <p>Description: {error_description}</p>
                </body>
                </html>
            """.encode())
        else:
            # Invalid callback
            self.send_response(400)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"""
                <html>
                <head><title>Invalid Request</title></head>
                <body>
                    <h1>Invalid Callback</h1>
                    <p>No authorization code or error received.</p>
                </body>
                </html>
            """)

    def log_message(self, format, *args):
        """Suppress server logs."""
        pass


class PKCEHelper:
    """Helper for generating PKCE parameters."""

    @staticmethod
    def generate_code_verifier() -> str:
        """Generate a PKCE code verifier."""
        return base64.urlsafe_b64encode(
            secrets.token_bytes(32)
        ).decode('utf-8').rstrip('=')

    @staticmethod
    def generate_code_challenge(verifier: str) -> str:
        """Generate a PKCE code challenge from verifier using S256."""
        digest = hashlib.sha256(verifier.encode('utf-8')).digest()
        return base64.urlsafe_b64encode(digest).decode('utf-8').rstrip('=')


class ClientStorage:
    """Persistent storage for OAuth client data."""

    def __init__(self, storage_path: Path):
        self.storage_path = storage_path
        self.data: Dict[str, Any] = {"clients": {}}
        self.load()

    def load(self):
        """Load client data from file."""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r') as f:
                    self.data = json.load(f)
                    if "clients" not in self.data:
                        self.data["clients"] = {}
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load storage file: {e}")
                self.data = {"clients": {}}

    def save(self):
        """Save client data to file."""
        try:
            # Create parent directory if it doesn't exist
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)

            with open(self.storage_path, 'w') as f:
                json.dump(self.data, f, indent=2)
        except IOError as e:
            print(f"Error: Could not save storage file: {e}")

    def get_client(self, server_url: str) -> Optional[Dict[str, Any]]:
        """Get client data for a server."""
        return self.data["clients"].get(server_url)

    def save_client(self, server_url: str, client_data: Dict[str, Any]):
        """Save client data for a server."""
        self.data["clients"][server_url] = client_data
        self.save()

    def list_clients(self) -> Dict[str, Dict[str, Any]]:
        """List all registered clients."""
        return self.data["clients"]

    def remove_client(self, server_url: str):
        """Remove a client."""
        if server_url in self.data["clients"]:
            del self.data["clients"][server_url]
            self.save()


class MCPOAuthClient:
    """MCP client with OAuth 2.0 and Dynamic Client Registration support."""

    def __init__(self, server_url: str, storage: ClientStorage, redirect_port: int = 3000):
        self.server_url = server_url.rstrip('/')
        self.storage = storage
        self.redirect_port = redirect_port
        self.redirect_uri = f"http://localhost:{redirect_port}/callback"

        # Client credentials
        self.client_id: Optional[str] = None
        self.client_secret: Optional[str] = None

        # OAuth tokens
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.token_expires_at: Optional[datetime] = None

        # PKCE parameters
        self.code_verifier: Optional[str] = None
        self.code_challenge: Optional[str] = None

        # Load existing client if available
        self._load_client()

    def _load_client(self):
        """Load client data from storage."""
        client_data = self.storage.get_client(self.server_url)
        if client_data:
            self.client_id = client_data.get("client_id")
            self.client_secret = client_data.get("client_secret")
            self.access_token = client_data.get("access_token")
            self.refresh_token = client_data.get("refresh_token")

            # Parse token expiration
            expires_str = client_data.get("token_expires_at")
            if expires_str:
                self.token_expires_at = datetime.fromisoformat(expires_str)

    def _save_client(self):
        """Save client data to storage."""
        client_data = {
            "server_url": self.server_url,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "token_expires_at": self.token_expires_at.isoformat() if self.token_expires_at else None,
            "registered_at": datetime.now().isoformat(),
        }
        self.storage.save_client(self.server_url, client_data)

    def discover_metadata(self) -> Dict[str, Any]:
        """Discover OAuth and MCP metadata from server."""
        print(f"\n📡 Discovering server metadata...")

        try:
            with httpx.Client() as client:
                # Try OAuth Authorization Server Metadata (RFC 8414)
                response = client.get(f"{self.server_url}/.well-known/oauth-authorization-server")
                if response.status_code == 200:
                    metadata = response.json()
                    print(f"✓ OAuth metadata discovered")
                    return metadata
        except httpx.RequestError as e:
            print(f"⚠ Could not discover metadata: {e}")

        # Fall back to default endpoints
        print(f"⚠ Using default endpoint locations")
        return {
            "issuer": self.server_url,
            "registration_endpoint": f"{self.server_url}/oauth/register",
            "authorization_endpoint": f"{self.server_url}/oauth/authorize",
            "token_endpoint": f"{self.server_url}/oauth/token",
        }

    def register_client(self, client_name: str = "MCP DCR Client", scopes: Optional[list] = None) -> bool:
        """Register client via Dynamic Client Registration (RFC 7591)."""
        print(f"\n🔐 Registering new OAuth client...")

        if scopes is None:
            scopes = ["mcp:tools:read", "mcp:tools:execute"]

        # Discover metadata
        metadata = self.discover_metadata()
        registration_endpoint = metadata.get("registration_endpoint")

        if not registration_endpoint:
            print("❌ No registration endpoint found")
            return False

        # Prepare registration request
        registration_request = {
            "redirect_uris": [self.redirect_uri],
            "client_name": client_name,
            "scope": " ".join(scopes),
        }

        try:
            with httpx.Client() as client:
                response = client.post(registration_endpoint, json=registration_request)

                if response.status_code == 200:
                    registration_response = response.json()
                    self.client_id = registration_response["client_id"]
                    self.client_secret = registration_response.get("client_secret")

                    print(f"✓ Client registered successfully")
                    print(f"  Client ID: {self.client_id}")
                    if self.client_secret:
                        print(f"  Client Secret: {self.client_secret[:10]}...")

                    # Save to storage
                    self._save_client()
                    return True
                else:
                    print(f"❌ Registration failed: {response.status_code}")
                    print(f"   {response.text}")
                    return False

        except httpx.RequestError as e:
            print(f"❌ Request error: {e}")
            return False

    def authorize(self) -> bool:
        """Perform OAuth 2.0 authorization code flow with PKCE."""
        print(f"\n🔑 Starting OAuth authorization flow...")

        if not self.client_id:
            print("❌ Client not registered. Run register_client() first.")
            return False

        # Discover metadata
        metadata = self.discover_metadata()
        authorization_endpoint = metadata.get("authorization_endpoint")
        token_endpoint = metadata.get("token_endpoint")

        if not authorization_endpoint or not token_endpoint:
            print("❌ Missing OAuth endpoints")
            return False

        # Generate PKCE parameters
        self.code_verifier = PKCEHelper.generate_code_verifier()
        self.code_challenge = PKCEHelper.generate_code_challenge(self.code_verifier)

        # Generate state for CSRF protection
        state = secrets.token_urlsafe(32)

        # Build authorization URL
        auth_params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": "mcp:tools:read mcp:tools:execute",
            "state": state,
            "code_challenge": self.code_challenge,
            "code_challenge_method": "S256",
        }

        auth_url = f"{authorization_endpoint}?{urlencode(auth_params)}"

        print(f"✓ Opening browser for authorization...")
        print(f"  If browser doesn't open, visit: {auth_url}")

        # Start local callback server
        server = HTTPServer(("localhost", self.redirect_port), OAuthCallbackHandler)

        # Reset callback handler state
        OAuthCallbackHandler.authorization_code = None
        OAuthCallbackHandler.state = None
        OAuthCallbackHandler.error = None

        # Open browser
        webbrowser.open(auth_url)

        # Wait for callback (with timeout)
        print(f"⏳ Waiting for authorization callback...")
        timeout = 120  # 2 minutes
        start_time = time.time()

        while time.time() - start_time < timeout:
            server.handle_request()

            # Check if we got a response
            if OAuthCallbackHandler.authorization_code:
                authorization_code = OAuthCallbackHandler.authorization_code
                returned_state = OAuthCallbackHandler.state

                # Validate state
                if returned_state != state:
                    print("❌ State mismatch - possible CSRF attack!")
                    return False

                print(f"✓ Authorization code received")

                # Exchange code for token
                return self._exchange_code_for_token(authorization_code, token_endpoint)

            elif OAuthCallbackHandler.error:
                print(f"❌ Authorization error: {OAuthCallbackHandler.error}")
                return False

        print("❌ Authorization timeout")
        return False

    def _exchange_code_for_token(self, authorization_code: str, token_endpoint: str) -> bool:
        """Exchange authorization code for access token."""
        print(f"\n🔄 Exchanging code for access token...")

        token_request = {
            "grant_type": "authorization_code",
            "code": authorization_code,
            "redirect_uri": self.redirect_uri,
            "code_verifier": self.code_verifier,
            "client_id": self.client_id,
        }

        try:
            with httpx.Client() as client:
                response = client.post(token_endpoint, data=token_request)

                if response.status_code == 200:
                    token_response = response.json()
                    self.access_token = token_response["access_token"]
                    self.refresh_token = token_response.get("refresh_token")

                    # Calculate token expiration by parsing JWT exp claim (timezone-safe)
                    # This ensures correct expiration regardless of client/server timezone
                    try:
                        from jose import jwt
                        claims = jwt.decode(
                            self.access_token,
                            options={"verify_signature": False}
                        )
                        self.token_expires_at = datetime.fromtimestamp(
                            claims['exp'],
                            tz=timezone.utc
                        ).replace(tzinfo=None)  # Store as naive UTC
                    except Exception:
                        # Fallback to expires_in if JWT parsing fails
                        expires_in = token_response.get("expires_in", 3600)
                        self.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

                    print(f"✓ Access token obtained")
                    print(f"  Token: {self.access_token[:30]}...")
                    print(f"  Expires: {self.token_expires_at.strftime('%Y-%m-%d %H:%M:%S')}")

                    # Save to storage
                    self._save_client()
                    return True
                else:
                    print(f"❌ Token exchange failed: {response.status_code}")
                    print(f"   {response.text}")
                    return False

        except httpx.RequestError as e:
            print(f"❌ Request error: {e}")
            return False

    def refresh_access_token(self) -> bool:
        """Refresh access token using refresh token."""
        print(f"\n🔄 Refreshing access token...")

        if not self.refresh_token:
            print("❌ No refresh token available")
            return False

        # Discover metadata
        metadata = self.discover_metadata()
        token_endpoint = metadata.get("token_endpoint")

        if not token_endpoint:
            print("❌ Token endpoint not found")
            return False

        refresh_request = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
            "client_id": self.client_id,
        }

        try:
            with httpx.Client() as client:
                response = client.post(token_endpoint, data=refresh_request)

                if response.status_code == 200:
                    token_response = response.json()
                    self.access_token = token_response["access_token"]

                    # Update expiration by parsing JWT exp claim (timezone-safe)
                    try:
                        from jose import jwt
                        claims = jwt.decode(
                            self.access_token,
                            options={"verify_signature": False}
                        )
                        self.token_expires_at = datetime.fromtimestamp(
                            claims['exp'],
                            tz=timezone.utc
                        ).replace(tzinfo=None)  # Store as naive UTC
                    except Exception:
                        # Fallback to expires_in if JWT parsing fails
                        expires_in = token_response.get("expires_in", 3600)
                        self.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

                    print(f"✓ Token refreshed successfully")
                    print(f"  New token: {self.access_token[:30]}...")

                    # Save to storage
                    self._save_client()
                    return True
                else:
                    print(f"❌ Token refresh failed: {response.status_code}")
                    print(f"   {response.text}")
                    return False

        except httpx.RequestError as e:
            print(f"❌ Request error: {e}")
            return False

    def ensure_valid_token(self) -> bool:
        """Ensure we have a valid access token, refreshing if necessary."""
        if not self.access_token:
            print("❌ No access token. Please authorize first.")
            return False

        # Check if token is expired or about to expire (within 5 minutes)
        # Use UTC to match server timezone
        if self.token_expires_at and datetime.utcnow() >= self.token_expires_at - timedelta(minutes=5):
            print("⚠ Token expired or expiring soon, refreshing...")
            return self.refresh_access_token()

        return True

    def list_tools(self) -> Optional[list]:
        """List available MCP tools."""
        print(f"\n🔧 Listing MCP tools...")

        if not self.ensure_valid_token():
            return None

        list_tools_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        }

        try:
            with httpx.Client() as client:
                response = client.post(
                    f"{self.server_url}/mcp/tools/list",
                    json=list_tools_request,
                    headers={"Authorization": f"Bearer {self.access_token}"}
                )

                if response.status_code == 200:
                    tools_response = response.json()
                    tools = tools_response.get("result", {}).get("tools", [])

                    print(f"✓ Found {len(tools)} tools:")
                    for tool in tools:
                        print(f"  - {tool['name']}: {tool['description']}")

                    return tools
                else:
                    print(f"❌ Failed to list tools: {response.status_code}")
                    print(f"   {response.text}")
                    return None

        except httpx.RequestError as e:
            print(f"❌ Request error: {e}")
            return None

    def call_tool(self, tool_name: str, arguments: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Call an MCP tool."""
        print(f"\n⚙️  Calling tool: {tool_name}")

        if not self.ensure_valid_token():
            return None

        if arguments is None:
            arguments = {}

        call_tool_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }

        try:
            with httpx.Client() as client:
                response = client.post(
                    f"{self.server_url}/mcp/tools/call",
                    json=call_tool_request,
                    headers={"Authorization": f"Bearer {self.access_token}"}
                )

                if response.status_code == 200:
                    tool_response = response.json()
                    result = tool_response.get("result", {})

                    print(f"✓ Tool executed successfully")
                    if "message" in result:
                        print(f"  Message: {result['message']}")
                    if "data" in result:
                        print(f"  Data: {json.dumps(result['data'], indent=2)}")

                    return result
                else:
                    print(f"❌ Tool call failed: {response.status_code}")
                    print(f"   {response.text}")
                    return None

        except httpx.RequestError as e:
            print(f"❌ Request error: {e}")
            return None


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="MCP OAuth DCR Client - Dynamic Client Registration and OAuth 2.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Register new client and authorize
  python client.py --server-url http://localhost:8000 --register --authorize

  # List tools
  python client.py --server-url http://localhost:8000 --list-tools

  # Call a tool
  python client.py --server-url http://localhost:8000 --call-tool get_weather --args '{"location": "San Francisco"}'

  # List all registered clients
  python client.py --list-clients

  # Full flow demo
  python client.py --server-url http://localhost:8000 --demo
        """
    )

    # Server options
    parser.add_argument("--server-url", help="MCP server URL")
    parser.add_argument("--storage", default=".mcp_clients.json", help="Storage file for client data")

    # Actions
    parser.add_argument("--register", action="store_true", help="Register new OAuth client")
    parser.add_argument("--authorize", action="store_true", help="Perform OAuth authorization")
    parser.add_argument("--list-tools", action="store_true", help="List available MCP tools")
    parser.add_argument("--call-tool", help="Call an MCP tool by name")
    parser.add_argument("--args", help="JSON arguments for tool call")
    parser.add_argument("--refresh", action="store_true", help="Refresh access token")
    parser.add_argument("--list-clients", action="store_true", help="List all registered clients")
    parser.add_argument("--remove-client", help="Remove a registered client by server URL")
    parser.add_argument("--demo", action="store_true", help="Run full demo flow")

    args = parser.parse_args()

    # Initialize storage
    storage_path = Path(args.storage)
    storage = ClientStorage(storage_path)

    # Handle list-clients
    if args.list_clients:
        print("\n📋 Registered Clients:")
        clients = storage.list_clients()
        if not clients:
            print("  No clients registered")
        else:
            for url, data in clients.items():
                print(f"\n  Server: {url}")
                print(f"    Client ID: {data.get('client_id')}")
                print(f"    Registered: {data.get('registered_at')}")
                if data.get('access_token'):
                    print(f"    Status: ✓ Authorized")
                else:
                    print(f"    Status: ⚠ Not authorized")
        return

    # Handle remove-client
    if args.remove_client:
        storage.remove_client(args.remove_client)
        print(f"✓ Removed client for {args.remove_client}")
        return

    # Require server URL for other actions
    if not args.server_url:
        parser.print_help()
        print("\nError: --server-url is required for most actions")
        sys.exit(1)

    # Initialize client
    client = MCPOAuthClient(args.server_url, storage)

    # Handle demo mode
    if args.demo:
        print("=" * 70)
        print("MCP OAuth DCR Client - Full Demo")
        print("=" * 70)

        # Step 1: Register
        if not client.client_id:
            print("\nStep 1: Client Registration")
            if not client.register_client():
                sys.exit(1)
        else:
            print(f"\n✓ Client already registered (ID: {client.client_id})")

        # Step 2: Authorize
        if not client.access_token:
            print("\nStep 2: OAuth Authorization")
            if not client.authorize():
                sys.exit(1)
        else:
            print(f"\n✓ Client already authorized")
            if not client.ensure_valid_token():
                sys.exit(1)

        # Step 3: List tools
        print("\nStep 3: List MCP Tools")
        tools = client.list_tools()
        if not tools:
            sys.exit(1)

        # Step 4: Call each tool
        print("\nStep 4: Call MCP Tools")

        # Call get_weather
        client.call_tool("get_weather", {"location": "San Francisco, CA", "units": "fahrenheit"})

        # Call list_files
        client.call_tool("list_files", {"path": "/home/user"})

        # Call get_user_profile
        client.call_tool("get_user_profile", {})

        # Step 5: Refresh token
        print("\nStep 5: Token Refresh")
        if client.refresh_access_token():
            print("✓ Token refreshed successfully")

            # Call another tool with new token
            client.call_tool("get_weather", {"location": "New York, NY", "units": "celsius"})

        print("\n" + "=" * 70)
        print("✅ Demo completed successfully!")
        print("=" * 70)
        return

    # Handle individual actions
    if args.register:
        if not client.register_client():
            sys.exit(1)

    if args.authorize:
        if not client.authorize():
            sys.exit(1)

    if args.refresh:
        if not client.refresh_access_token():
            sys.exit(1)

    if args.list_tools:
        if not client.list_tools():
            sys.exit(1)

    if args.call_tool:
        tool_args = {}
        if args.args:
            try:
                tool_args = json.loads(args.args)
            except json.JSONDecodeError as e:
                print(f"Error: Invalid JSON arguments: {e}")
                sys.exit(1)

        if not client.call_tool(args.call_tool, tool_args):
            sys.exit(1)


if __name__ == "__main__":
    main()
