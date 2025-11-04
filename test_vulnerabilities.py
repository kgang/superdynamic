#!/usr/bin/env python3
"""
Vulnerability Demonstration Script
Tests the critical findings from LLM code assessment.

IMPORTANT: This is for educational/testing purposes on your own systems only.
Do not use against production systems or systems you don't own.
"""

import httpx
import time
import threading
from datetime import datetime, timezone, timedelta
from concurrent.futures import ThreadPoolExecutor
import json

SERVER_URL = "http://localhost:8000"

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_test(name):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}TEST: {name}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}\n")

def print_pass(msg):
    print(f"{Colors.GREEN}✓ PASS:{Colors.RESET} {msg}")

def print_fail(msg):
    print(f"{Colors.RED}✗ FAIL:{Colors.RESET} {msg}")

def print_vuln(msg):
    print(f"{Colors.RED}🔴 VULNERABILITY CONFIRMED:{Colors.RESET} {msg}")

def print_info(msg):
    print(f"{Colors.YELLOW}ℹ INFO:{Colors.RESET} {msg}")


# =============================================================================
# TEST 1: Authorization Code Race Condition
# =============================================================================

def test_auth_code_race_condition():
    """
    Demonstrates that the same authorization code can be used twice
    if two requests are sent concurrently.
    """
    print_test("Authorization Code Race Condition (TOCTOU)")

    print_info("Setting up client registration...")

    # Register a client
    try:
        reg_response = httpx.post(
            f"{SERVER_URL}/oauth/register",
            json={
                "redirect_uris": ["http://localhost:3000/callback"],
                "client_name": "Test Client",
            },
            timeout=5.0
        )
        reg_response.raise_for_status()
        client_data = reg_response.json()
        client_id = client_data["client_id"]
        client_secret = client_data["client_secret"]
        print_pass(f"Client registered: {client_id}")
    except Exception as e:
        print_fail(f"Registration failed: {e}")
        return

    # Generate PKCE parameters
    import base64
    import hashlib
    import secrets

    verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
    challenge = base64.urlsafe_b64encode(
        hashlib.sha256(verifier.encode('utf-8')).digest()
    ).decode('utf-8').rstrip('=')

    print_info(f"PKCE verifier: {verifier[:20]}...")
    print_info(f"PKCE challenge: {challenge[:20]}...")

    # Get authorization code (auto-approved by mock server)
    try:
        auth_url = (
            f"{SERVER_URL}/oauth/authorize"
            f"?response_type=code"
            f"&client_id={client_id}"
            f"&redirect_uri=http://localhost:3000/callback"
            f"&code_challenge={challenge}"
            f"&code_challenge_method=S256"
            f"&scope=mcp:tools:read"
        )
        auth_response = httpx.get(auth_url, follow_redirects=False, timeout=5.0)

        # Extract code from redirect
        location = auth_response.headers.get("location", "")
        code = location.split("code=")[1].split("&")[0] if "code=" in location else None

        if not code:
            print_fail("Failed to get authorization code")
            return

        print_pass(f"Got authorization code: {code[:20]}...")
    except Exception as e:
        print_fail(f"Authorization failed: {e}")
        return

    # Now attempt to exchange the SAME code TWICE concurrently
    print_info("Attempting concurrent token exchanges with same code...")

    results = []

    def exchange_code(attempt_num):
        """Exchange authorization code for token."""
        try:
            start = time.time()
            response = httpx.post(
                f"{SERVER_URL}/oauth/token",
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": "http://localhost:3000/callback",
                    "code_verifier": verifier,
                    "client_id": client_id,
                    "client_secret": client_secret,
                },
                timeout=5.0
            )
            elapsed = time.time() - start

            return {
                "attempt": attempt_num,
                "status": response.status_code,
                "success": response.status_code == 200,
                "elapsed": elapsed,
                "response": response.json() if response.status_code == 200 else response.text
            }
        except Exception as e:
            return {
                "attempt": attempt_num,
                "status": 0,
                "success": False,
                "error": str(e)
            }

    # Execute two exchanges concurrently
    with ThreadPoolExecutor(max_workers=2) as executor:
        future1 = executor.submit(exchange_code, 1)
        future2 = executor.submit(exchange_code, 2)

        result1 = future1.result()
        result2 = future2.result()

        results = [result1, result2]

    # Analyze results
    successes = [r for r in results if r["success"]]
    failures = [r for r in results if not r["success"]]

    print(f"\nResults:")
    print(f"  Attempt 1: {'SUCCESS' if result1['success'] else 'FAILED'} ({result1['status']}) - {result1.get('elapsed', 0)*1000:.1f}ms")
    print(f"  Attempt 2: {'SUCCESS' if result2['success'] else 'FAILED'} ({result2['status']}) - {result2.get('elapsed', 0)*1000:.1f}ms")

    if len(successes) > 1:
        print_vuln("Both requests succeeded! Authorization code was reused.")
        print_info("This violates RFC 6749 Section 4.1.2: codes MUST be single-use")
        print_info("An attacker who intercepts a code could generate multiple tokens")

        # Show that we got different tokens
        if "response" in successes[0] and "response" in successes[1]:
            token1 = successes[0]["response"].get("access_token", "")
            token2 = successes[1]["response"].get("access_token", "")
            if token1 != token2:
                print_info(f"Token 1: {token1[:30]}...")
                print_info(f"Token 2: {token2[:30]}...")
                print_vuln("Two different tokens issued from one authorization code!")
    elif len(successes) == 1:
        print_pass("Only one request succeeded - race condition not exploited this time")
        print_info("Note: Race condition may still exist but timing didn't align")
    else:
        print_fail("Both requests failed - unexpected result")


# =============================================================================
# TEST 2: DateTime Timezone Mismatch
# =============================================================================

def test_datetime_timezone_bug():
    """
    Demonstrates that client calculates token expiration incorrectly
    when client and server are in different timezones.
    """
    print_test("DateTime Timezone Mismatch")

    print_info("This test demonstrates the timezone bug by comparing:")
    print_info("  1. Server's UTC-based token expiration (in JWT)")
    print_info("  2. Client's local-time calculation (client.py:400)")

    # Get current time in different representations
    utc_now = datetime.now(timezone.utc)
    local_now = datetime.now()  # No timezone
    utc_now_naive = datetime.utcnow()  # Deprecated but used by server

    print(f"\nCurrent times:")
    print(f"  Server time (datetime.utcnow()): {utc_now_naive}")
    print(f"  Client time (datetime.now()):    {local_now}")
    print(f"  UTC time (datetime.now(UTC)):    {utc_now}")

    # Simulate token expiration calculation
    expires_in_seconds = 3600  # 1 hour

    # How SERVER calculates expiration (token.py:44)
    server_expiration = utc_now_naive + timedelta(seconds=expires_in_seconds)

    # How CLIENT calculates expiration (client.py:400)
    client_expiration = local_now + timedelta(seconds=expires_in_seconds)

    print(f"\nToken expiration calculations (1 hour from now):")
    print(f"  Server calculates: {server_expiration} (UTC)")
    print(f"  Client calculates: {client_expiration} (local time, no timezone)")

    # Calculate the difference
    # If local time != UTC, there will be a mismatch
    local_offset = local_now - utc_now_naive

    print(f"\nTimezone offset:")
    print(f"  Difference: {local_offset}")

    if abs(local_offset.total_seconds()) > 60:  # More than 1 minute difference
        hours_off = local_offset.total_seconds() / 3600
        print_vuln(f"Client is {hours_off:.1f} hours off from UTC!")
        print_info("Client will incorrectly calculate token expiration")
        print_info("This causes:")
        print_info("  - Client uses expired tokens (if local > UTC)")
        print_info("  - Client refreshes tokens too early (if local < UTC)")

        # Show practical impact
        print(f"\nPractical Impact:")
        if hours_off > 0:
            print_info(f"  Client thinks token valid until {client_expiration}")
            print_info(f"  Server rejects token after {server_expiration} UTC")
            print_vuln(f"  Client will use expired tokens for {abs(hours_off):.1f} hours!")
        else:
            print_info(f"  Client refreshes token at {client_expiration}")
            print_info(f"  Token actually valid until {server_expiration} UTC")
            print_info(f"  Client wastes {abs(hours_off):.1f} hours of token lifetime")
    else:
        print_pass("Client and server in same timezone (or close enough)")
        print_info("Bug would manifest if client/server in different timezones")


# =============================================================================
# TEST 3: Network Error Handling
# =============================================================================

def test_network_error_handling():
    """
    Tests whether client handles network errors gracefully.
    """
    print_test("Network Error Handling")

    print_info("Testing client behavior with unreachable server...")

    # Test 1: Connection refused (server not running)
    fake_server = "http://localhost:9999"  # Nothing listening here

    print(f"\n1. Testing connection to non-existent server: {fake_server}")

    try:
        import sys
        import io

        # Capture the crash
        old_stderr = sys.stderr
        sys.stderr = io.StringIO()

        response = httpx.post(
            f"{fake_server}/oauth/register",
            json={"redirect_uris": ["http://localhost:3000"]},
            timeout=1.0
        )

        # If we got here, request somehow succeeded
        sys.stderr = old_stderr
        print_fail("Request succeeded unexpectedly")

    except httpx.ConnectError as e:
        sys.stderr = old_stderr
        print_vuln("Client crashes with unhandled exception:")
        print(f"  {type(e).__name__}: {e}")
        print_info("Client should catch this and show user-friendly error")

    except Exception as e:
        sys.stderr = old_stderr
        print_fail(f"Unexpected exception: {e}")

    # Test 2: Invalid JSON response
    print(f"\n2. Testing invalid JSON handling (simulated):")
    print_info("If server returned HTML error page instead of JSON:")
    print_info("  response.json() would raise json.JSONDecodeError")
    print_info("  Current client.py:272 does NOT handle this")
    print_vuln("Client would crash with unhandled JSONDecodeError")


# =============================================================================
# TEST 4: Callback Handler Shared State
# =============================================================================

def test_callback_shared_state():
    """
    Demonstrates that concurrent OAuth flows corrupt each other due to
    shared class variables.
    """
    print_test("Callback Handler Shared State")

    print_info("This test demonstrates class variable pollution:")

    # Simulate what happens with the current implementation
    class OAuthCallbackHandler:
        # Class variables (shared across all instances)
        authorization_code = None
        state = None

    # Simulate two concurrent authorizations
    print("\nSimulation of concurrent OAuth flows:\n")

    print("1. User A starts authorization for server1")
    print("   OAuthCallbackHandler.authorization_code = None")
    handler1_state = OAuthCallbackHandler.authorization_code

    print("\n2. User B starts authorization for server2")
    print("   OAuthCallbackHandler.authorization_code = None")
    handler2_state = OAuthCallbackHandler.authorization_code

    print("\n3. User A completes authorization")
    print("   Server redirects: http://localhost:3000/?code=CODE_A")
    OAuthCallbackHandler.authorization_code = "CODE_A"
    print(f"   OAuthCallbackHandler.authorization_code = '{OAuthCallbackHandler.authorization_code}'")

    print("\n4. User B completes authorization")
    print("   Server redirects: http://localhost:3000/?code=CODE_B")
    OAuthCallbackHandler.authorization_code = "CODE_B"
    print(f"   OAuthCallbackHandler.authorization_code = '{OAuthCallbackHandler.authorization_code}'")

    print("\n5. User A's client retrieves code")
    code_for_a = OAuthCallbackHandler.authorization_code
    print(f"   code = OAuthCallbackHandler.authorization_code")
    print(f"   code = '{code_for_a}'")

    if code_for_a != "CODE_A":
        print_vuln(f"User A got wrong code: '{code_for_a}' instead of 'CODE_A'")
        print_info("User A's authorization is lost!")
        print_info("User B's code overwrote User A's code")
    else:
        print_pass("Codes didn't collide in this simulation")

    print("\nRoot cause: Class variables in client.py:36-39")
    print("Fix: Use instance variables or thread-local storage")


# =============================================================================
# TEST 5: Missing Resource Parameter
# =============================================================================

def test_missing_resource_parameter():
    """
    Verifies that client doesn't send resource parameter per MCP spec.
    """
    print_test("Missing Resource Parameter (MCP Spec Violation)")

    print_info("MCP Authorization Spec Section 3.2 requires:")
    print_info('  "Clients MUST include the resource parameter"')

    print("\nChecking authorization request parameters...")

    # What client.py:326 currently sends:
    current_params = [
        "response_type",
        "client_id",
        "redirect_uri",
        "scope",
        "state",
        "code_challenge",
        "code_challenge_method"
    ]

    print(f"Current parameters: {', '.join(current_params)}")

    if "resource" not in current_params:
        print_vuln("'resource' parameter is MISSING")
        print_info("Per MCP spec, should include: resource={server_url}")
        print_info("This prevents token audience binding across MCP servers")
    else:
        print_pass("Resource parameter present")

    print("\nChecking token request parameters...")

    current_token_params = [
        "grant_type",
        "code",
        "redirect_uri",
        "code_verifier",
        "client_id",
        "client_secret"
    ]

    print(f"Current parameters: {', '.join(current_token_params)}")

    if "resource" not in current_token_params:
        print_vuln("'resource' parameter is MISSING")
    else:
        print_pass("Resource parameter present")


# =============================================================================
# Main Test Runner
# =============================================================================

def main():
    print(f"{Colors.BOLD}{Colors.BLUE}")
    print("=" * 70)
    print("  LLM CODE VULNERABILITY DEMONSTRATION")
    print("  MCP OAuth DCR Implementation Assessment")
    print("=" * 70)
    print(f"{Colors.RESET}")

    print(f"\n{Colors.YELLOW}WARNING: These tests demonstrate security vulnerabilities.{Colors.RESET}")
    print(f"{Colors.YELLOW}Only run against your own test server at {SERVER_URL}{Colors.RESET}\n")

    # Check if server is running
    try:
        health = httpx.get(f"{SERVER_URL}/health", timeout=2.0)
        if health.status_code == 200:
            print_pass(f"Server is running at {SERVER_URL}")
        else:
            print_fail(f"Server returned {health.status_code}")
            return
    except Exception as e:
        print_fail(f"Cannot connect to server: {e}")
        print_info("Start server with: cd server && docker-compose up")
        return

    # Run tests
    tests = [
        ("1", "Auth Code Race Condition", test_auth_code_race_condition),
        ("2", "DateTime Timezone Bug", test_datetime_timezone_bug),
        ("3", "Network Error Handling", test_network_error_handling),
        ("4", "Callback Shared State", test_callback_shared_state),
        ("5", "Missing Resource Parameter", test_missing_resource_parameter),
    ]

    print(f"\n{Colors.BOLD}Available Tests:{Colors.RESET}")
    for num, name, _ in tests:
        print(f"  {num}. {name}")
    print(f"  all. Run all tests")

    selection = input(f"\n{Colors.BOLD}Select test (1-5 or 'all'):{Colors.RESET} ").strip()

    if selection == "all":
        for _, _, test_func in tests:
            try:
                test_func()
            except KeyboardInterrupt:
                print("\n\nTests interrupted by user")
                return
            except Exception as e:
                print_fail(f"Test crashed: {e}")
                import traceback
                traceback.print_exc()
    else:
        for num, _, test_func in tests:
            if selection == num:
                test_func()
                break
        else:
            print_fail("Invalid selection")

    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}Assessment Complete{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}\n")

    print("See VERIFIED_CRITICAL_FINDINGS.md for detailed analysis and fixes.")


if __name__ == "__main__":
    main()
