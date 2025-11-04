"""
End-to-end flow test for MCP OAuth DCR Server.

This test demonstrates the complete OAuth + MCP flow:
1. Dynamic Client Registration
2. Authorization Request
3. Token Exchange (with PKCE)
4. MCP Tool Invocation
5. Token Refresh
"""

import httpx
import hashlib
import base64
import secrets
from urllib.parse import urlparse, parse_qs


class TestOAuthMCPFlow:
    """Test the complete OAuth + MCP authorization flow."""

    BASE_URL = "http://localhost:8000"

    @staticmethod
    def generate_pkce_pair():
        """Generate PKCE code verifier and challenge."""
        # Generate code verifier
        code_verifier = base64.urlsafe_b64encode(
            secrets.token_bytes(32)
        ).decode('utf-8').rstrip('=')

        # Generate code challenge (S256)
        digest = hashlib.sha256(code_verifier.encode('utf-8')).digest()
        code_challenge = base64.urlsafe_b64encode(digest).decode('utf-8').rstrip('=')

        return code_verifier, code_challenge

    def test_complete_flow(self):
        """Test the complete OAuth + MCP flow."""
        with httpx.Client() as client:
            # ================================================================
            # Step 1: Dynamic Client Registration (RFC 7591)
            # ================================================================
            print("\n" + "=" * 60)
            print("Step 1: Dynamic Client Registration")
            print("=" * 60)

            registration_request = {
                "redirect_uris": ["http://localhost:3000/callback"],
                "client_name": "Test MCP Client",
                "scope": "mcp:tools:read mcp:tools:execute",
            }

            response = client.post(
                f"{self.BASE_URL}/oauth/register",
                json=registration_request
            )

            assert response.status_code == 200
            registration_response = response.json()

            client_id = registration_response["client_id"]
            client_secret = registration_response["client_secret"]

            print(f"✓ Client registered successfully")
            print(f"  Client ID: {client_id}")
            print(f"  Client Secret: {client_secret[:10]}...")

            # ================================================================
            # Step 2: Generate PKCE Parameters
            # ================================================================
            print("\n" + "=" * 60)
            print("Step 2: Generate PKCE Parameters")
            print("=" * 60)

            code_verifier, code_challenge = self.generate_pkce_pair()

            print(f"✓ PKCE parameters generated")
            print(f"  Code Verifier: {code_verifier[:20]}...")
            print(f"  Code Challenge: {code_challenge[:20]}...")

            # ================================================================
            # Step 3: Authorization Request
            # ================================================================
            print("\n" + "=" * 60)
            print("Step 3: Authorization Request")
            print("=" * 60)

            auth_params = {
                "response_type": "code",
                "client_id": client_id,
                "redirect_uri": "http://localhost:3000/callback",
                "scope": "mcp:tools:read mcp:tools:execute",
                "state": "random_state_123",
                "code_challenge": code_challenge,
                "code_challenge_method": "S256",
            }

            # Note: follow_redirects=False to capture the redirect
            response = client.get(
                f"{self.BASE_URL}/oauth/authorize",
                params=auth_params,
                follow_redirects=False
            )

            assert response.status_code == 307  # Redirect
            redirect_url = response.headers["location"]

            # Extract authorization code from redirect
            parsed_url = urlparse(redirect_url)
            query_params = parse_qs(parsed_url.query)
            authorization_code = query_params["code"][0]
            returned_state = query_params["state"][0]

            assert returned_state == "random_state_123"

            print(f"✓ Authorization code obtained")
            print(f"  Code: {authorization_code[:20]}...")
            print(f"  State verified: {returned_state}")

            # ================================================================
            # Step 4: Token Exchange (with PKCE validation)
            # ================================================================
            print("\n" + "=" * 60)
            print("Step 4: Token Exchange")
            print("=" * 60)

            token_request = {
                "grant_type": "authorization_code",
                "code": authorization_code,
                "redirect_uri": "http://localhost:3000/callback",
                "code_verifier": code_verifier,
                "client_id": client_id,
            }

            response = client.post(
                f"{self.BASE_URL}/oauth/token",
                data=token_request
            )

            if response.status_code != 200:
                print(f"\n❌ Token exchange failed!")
                print(f"  Status Code: {response.status_code}")
                print(f"  Response Body: {response.text}")
                print(f"  Request Data: {token_request}")

            assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.text}"
            token_response = response.json()

            access_token = token_response["access_token"]
            refresh_token = token_response["refresh_token"]

            print(f"✓ Tokens obtained successfully")
            print(f"  Access Token: {access_token[:30]}...")
            print(f"  Refresh Token: {refresh_token[:30]}...")
            print(f"  Expires In: {token_response['expires_in']} seconds")

            # ================================================================
            # Step 5: MCP Initialize (no auth required)
            # ================================================================
            print("\n" + "=" * 60)
            print("Step 5: MCP Initialize")
            print("=" * 60)

            initialize_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "0.1.0",
                    "clientInfo": {
                        "name": "Test Client",
                        "version": "1.0.0"
                    }
                }
            }

            response = client.post(
                f"{self.BASE_URL}/mcp/initialize",
                json=initialize_request
            )

            assert response.status_code == 200
            initialize_response = response.json()

            print(f"✓ MCP initialized")
            print(f"  Server: {initialize_response['result']['serverInfo']['name']}")
            print(f"  Version: {initialize_response['result']['serverInfo']['version']}")

            # ================================================================
            # Step 6: List MCP Tools (requires auth)
            # ================================================================
            print("\n" + "=" * 60)
            print("Step 6: List MCP Tools")
            print("=" * 60)

            list_tools_request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {}
            }

            response = client.post(
                f"{self.BASE_URL}/mcp/tools/list",
                json=list_tools_request,
                headers={"Authorization": f"Bearer {access_token}"}
            )

            assert response.status_code == 200
            tools_response = response.json()

            print(f"✓ Tools listed successfully")
            for tool in tools_response["result"]["tools"]:
                print(f"  - {tool['name']}: {tool['description']}")

            # ================================================================
            # Step 7: Call MCP Tool (requires auth)
            # ================================================================
            print("\n" + "=" * 60)
            print("Step 7: Call MCP Tool - get_weather")
            print("=" * 60)

            call_tool_request = {
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

            response = client.post(
                f"{self.BASE_URL}/mcp/tools/call",
                json=call_tool_request,
                headers={"Authorization": f"Bearer {access_token}"}
            )

            assert response.status_code == 200
            tool_response = response.json()

            print(f"✓ Tool executed successfully")
            print(f"  Result: {tool_response['result']['message']}")
            print(f"  Data: {tool_response['result']['data']}")

            # ================================================================
            # Step 8: Refresh Token
            # ================================================================
            print("\n" + "=" * 60)
            print("Step 8: Refresh Access Token")
            print("=" * 60)

            refresh_request = {
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "client_id": client_id,
            }

            response = client.post(
                f"{self.BASE_URL}/oauth/token",
                data=refresh_request
            )

            assert response.status_code == 200
            refresh_response = response.json()

            new_access_token = refresh_response["access_token"]

            print(f"✓ Token refreshed successfully")
            print(f"  New Access Token: {new_access_token[:30]}...")

            # ================================================================
            # Step 9: Use New Token for Another Tool Call
            # ================================================================
            print("\n" + "=" * 60)
            print("Step 9: Call Another Tool with New Token")
            print("=" * 60)

            call_tool_request = {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {
                    "name": "get_user_profile",
                    "arguments": {}
                }
            }

            response = client.post(
                f"{self.BASE_URL}/mcp/tools/call",
                json=call_tool_request,
                headers={"Authorization": f"Bearer {new_access_token}"}
            )

            assert response.status_code == 200
            profile_response = response.json()

            print(f"✓ Tool executed with new token")
            print(f"  User: {profile_response['result']['data']['username']}")
            print(f"  Email: {profile_response['result']['data']['email']}")

            print("\n" + "=" * 60)
            print("✅ ALL TESTS PASSED!")
            print("=" * 60)


if __name__ == "__main__":
    import sys
    import time

    # Add retry logic for CI/CD environments where server might need extra time
    max_retries = 3
    retry_delay = 2

    for attempt in range(max_retries):
        try:
            # Quick health check before running tests
            with httpx.Client() as client:
                try:
                    response = client.get(f"{TestOAuthMCPFlow.BASE_URL}/health", timeout=5.0)
                    if response.status_code != 200:
                        if attempt < max_retries - 1:
                            print(f"⚠ Server health check failed (attempt {attempt + 1}/{max_retries}), retrying in {retry_delay}s...")
                            time.sleep(retry_delay)
                            continue
                        else:
                            print("❌ Server health check failed after all retries")
                            sys.exit(1)
                except httpx.ConnectError:
                    if attempt < max_retries - 1:
                        print(f"⚠ Cannot connect to server (attempt {attempt + 1}/{max_retries}), retrying in {retry_delay}s...")
                        time.sleep(retry_delay)
                        continue
                    else:
                        print(f"❌ ERROR: Cannot connect to server at {TestOAuthMCPFlow.BASE_URL}")
                        print("   Make sure the server is running:")
                        print("   cd server && uvicorn app.main:app --reload")
                        sys.exit(1)

            # Run the test
            test = TestOAuthMCPFlow()
            test.test_complete_flow()
            print("\n✅ Test suite completed successfully")
            sys.exit(0)

        except AssertionError as e:
            print(f"\n❌ Test assertion failed: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
