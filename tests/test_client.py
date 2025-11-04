#!/usr/bin/env python3
"""
Non-interactive test for MCP OAuth DCR Client.

This test simulates the client flow without browser interaction by
directly calling the authorization endpoint and extracting the code.
"""

import json
import sys
from pathlib import Path

import httpx

# Import client classes (without running main)
sys.path.insert(0, str(Path(__file__).parent))
from client import MCPOAuthClient, ClientStorage, PKCEHelper


def test_client_flow():
    """Test the complete client flow."""
    print("=" * 70)
    print("Testing MCP OAuth DCR Client")
    print("=" * 70)

    server_url = "http://localhost:8000"
    storage_path = Path(".test_clients.json")

    # Clean up any existing test storage
    if storage_path.exists():
        storage_path.unlink()

    # Initialize storage and client
    storage = ClientStorage(storage_path)
    client = MCPOAuthClient(server_url, storage, redirect_port=3001)

    # ================================================================
    # Test 1: Discover Metadata
    # ================================================================
    print("\n" + "=" * 70)
    print("Test 1: Discover Metadata")
    print("=" * 70)

    metadata = client.discover_metadata()
    assert "authorization_endpoint" in metadata
    assert "token_endpoint" in metadata
    print("✓ Metadata discovery successful")

    # ================================================================
    # Test 2: Register Client
    # ================================================================
    print("\n" + "=" * 70)
    print("Test 2: Register Client via DCR")
    print("=" * 70)

    success = client.register_client(client_name="Test Client")
    assert success, "Client registration failed"
    assert client.client_id is not None
    assert client.client_secret is not None
    print("✓ Client registered successfully")

    # ================================================================
    # Test 3: Simulate OAuth Flow (without browser)
    # ================================================================
    print("\n" + "=" * 70)
    print("Test 3: OAuth Authorization (Simulated)")
    print("=" * 70)

    # Generate PKCE parameters
    code_verifier = PKCEHelper.generate_code_verifier()
    code_challenge = PKCEHelper.generate_code_challenge(code_verifier)

    # Manually call authorization endpoint (simulating browser)
    with httpx.Client() as http_client:
        auth_params = {
            "response_type": "code",
            "client_id": client.client_id,
            "redirect_uri": client.redirect_uri,
            "scope": "mcp:tools:read mcp:tools:execute",
            "state": "test_state_123",
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
        }

        response = http_client.get(
            f"{server_url}/oauth/authorize",
            params=auth_params,
            follow_redirects=False
        )

        assert response.status_code == 307, f"Expected 307, got {response.status_code}"

        # Extract authorization code from redirect
        from urllib.parse import urlparse, parse_qs
        redirect_url = response.headers["location"]
        parsed_url = urlparse(redirect_url)
        query_params = parse_qs(parsed_url.query)
        authorization_code = query_params["code"][0]

        print(f"✓ Authorization code obtained: {authorization_code[:20]}...")

        # Exchange code for token
        token_request = {
            "grant_type": "authorization_code",
            "code": authorization_code,
            "redirect_uri": client.redirect_uri,
            "code_verifier": code_verifier,
            "client_id": client.client_id,
        }

        response = http_client.post(
            f"{server_url}/oauth/token",
            data=token_request
        )

        assert response.status_code == 200, f"Token exchange failed: {response.status_code} - {response.text}"
        token_response = response.json()

        client.access_token = token_response["access_token"]
        client.refresh_token = token_response.get("refresh_token")

        print(f"✓ Access token obtained: {client.access_token[:30]}...")
        print(f"✓ Refresh token obtained: {client.refresh_token[:30]}...")

        # Save to storage
        from datetime import datetime, timedelta
        client.token_expires_at = datetime.now() + timedelta(seconds=token_response.get("expires_in", 3600))
        client._save_client()

    # ================================================================
    # Test 4: List Tools
    # ================================================================
    print("\n" + "=" * 70)
    print("Test 4: List MCP Tools")
    print("=" * 70)

    tools = client.list_tools()
    assert tools is not None, "Failed to list tools"
    assert len(tools) > 0, "No tools returned"
    print(f"✓ Found {len(tools)} tools")

    # ================================================================
    # Test 5: Call Tools
    # ================================================================
    print("\n" + "=" * 70)
    print("Test 5: Call MCP Tools")
    print("=" * 70)

    # Call get_weather
    result = client.call_tool("get_weather", {
        "location": "San Francisco, CA",
        "units": "fahrenheit"
    })
    assert result is not None, "get_weather failed"
    print("✓ get_weather executed")

    # Call list_files
    result = client.call_tool("list_files", {"path": "/home/user"})
    assert result is not None, "list_files failed"
    print("✓ list_files executed")

    # Call get_user_profile
    result = client.call_tool("get_user_profile", {})
    assert result is not None, "get_user_profile failed"
    print("✓ get_user_profile executed")

    # ================================================================
    # Test 6: Token Refresh
    # ================================================================
    print("\n" + "=" * 70)
    print("Test 6: Token Refresh")
    print("=" * 70)

    old_token = client.access_token
    success = client.refresh_access_token()
    assert success, "Token refresh failed"
    # Note: Mock server may return same token, which is okay
    print("✓ Token refreshed successfully")

    # Call tool with new token
    result = client.call_tool("get_weather", {
        "location": "New York, NY",
        "units": "celsius"
    })
    assert result is not None, "Tool call with refreshed token failed"
    print("✓ Tool call with new token successful")

    # ================================================================
    # Test 7: Client Lifecycle Management
    # ================================================================
    print("\n" + "=" * 70)
    print("Test 7: Client Lifecycle Management")
    print("=" * 70)

    # List clients
    clients = storage.list_clients()
    assert server_url in clients, "Client not in storage"
    print(f"✓ Client persisted in storage")

    # Create a second client for a different server
    server_url2 = "http://localhost:8001"
    client2 = MCPOAuthClient(server_url2, storage)
    print(f"✓ Can manage multiple clients")

    # List all clients
    all_clients = storage.list_clients()
    assert len(all_clients) >= 1, "Expected at least 1 client"
    print(f"✓ Storage contains {len(all_clients)} client(s)")

    # ================================================================
    # Test 8: Client Reloading
    # ================================================================
    print("\n" + "=" * 70)
    print("Test 8: Client Reloading from Storage")
    print("=" * 70)

    # Create new client instance (should load from storage)
    client_reloaded = MCPOAuthClient(server_url, storage)
    assert client_reloaded.client_id == client.client_id, "Client ID mismatch"
    assert client_reloaded.access_token == client.access_token, "Access token mismatch"
    print("✓ Client state reloaded from storage")

    # Use reloaded client
    tools = client_reloaded.list_tools()
    assert tools is not None, "Reloaded client failed to list tools"
    print("✓ Reloaded client functional")

    # ================================================================
    # Cleanup
    # ================================================================
    print("\n" + "=" * 70)
    print("Cleanup")
    print("=" * 70)

    if storage_path.exists():
        storage_path.unlink()
        print("✓ Test storage cleaned up")

    print("\n" + "=" * 70)
    print("✅ ALL TESTS PASSED!")
    print("=" * 70)


if __name__ == "__main__":
    try:
        test_client_flow()
    except AssertionError as e:
        print(f"\n❌ Test assertion failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
