"""
Pytest configuration and fixtures for MCP OAuth DCR tests.
"""
import pytest
import httpx
import time
from typing import Dict, Any


@pytest.fixture(scope="session")
def server_url():
    """Base URL for the test server."""
    return "http://localhost:8000"


@pytest.fixture(scope="session")
def server_health_check(server_url):
    """
    Verify server is running before tests.
    Fails fast if server is not accessible.
    """
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            response = httpx.get(f"{server_url}/health", timeout=2.0)
            if response.status_code == 200:
                return True
        except Exception:
            if attempt < max_attempts - 1:
                time.sleep(1)
            else:
                pytest.fail(
                    f"Server not accessible at {server_url}. "
                    "Please start the server: cd server && docker-compose up"
                )
    return False


@pytest.fixture
def client_factory(server_url):
    """
    Factory for creating test OAuth clients.
    Returns a function that registers a new client.
    """
    def create_client(client_name: str = "Test Client") -> Dict[str, Any]:
        """Register a new OAuth client and return credentials."""
        response = httpx.post(
            f"{server_url}/oauth/register",
            json={
                "redirect_uris": ["http://localhost:3000/callback"],
                "client_name": client_name,
            },
            timeout=5.0
        )
        response.raise_for_status()
        return response.json()

    return create_client


@pytest.fixture
def pkce_params():
    """Generate PKCE code verifier and challenge for testing."""
    import base64
    import hashlib
    import secrets

    verifier = base64.urlsafe_b64encode(
        secrets.token_bytes(32)
    ).decode('utf-8').rstrip('=')

    challenge = base64.urlsafe_b64encode(
        hashlib.sha256(verifier.encode('utf-8')).digest()
    ).decode('utf-8').rstrip('=')

    return {
        "verifier": verifier,
        "challenge": challenge,
        "method": "S256"
    }


@pytest.fixture
def auth_code_factory(server_url, client_factory, pkce_params):
    """
    Factory for obtaining authorization codes.
    Returns a function that gets an auth code for a client.
    """
    def get_auth_code(client_id: str = None) -> Dict[str, Any]:
        """Get authorization code via auto-approval flow."""
        if client_id is None:
            client = client_factory()
            client_id = client["client_id"]
        else:
            client = {"client_id": client_id}

        # Request authorization (auto-approved by mock server)
        auth_url = (
            f"{server_url}/oauth/authorize"
            f"?response_type=code"
            f"&client_id={client_id}"
            f"&redirect_uri=http://localhost:3000/callback"
            f"&code_challenge={pkce_params['challenge']}"
            f"&code_challenge_method={pkce_params['method']}"
            f"&scope=mcp:tools:read"
        )

        response = httpx.get(auth_url, follow_redirects=False, timeout=5.0)

        # Extract code from redirect
        location = response.headers.get("location", "")
        code = None
        if "code=" in location:
            code = location.split("code=")[1].split("&")[0]

        return {
            "code": code,
            "client_id": client_id,
            "verifier": pkce_params["verifier"],
            "redirect_uri": "http://localhost:3000/callback"
        }

    return get_auth_code
