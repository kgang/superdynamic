# Complete Authorization Flow Diagram

This document provides a detailed, step-by-step visualization of the OAuth 2.0 + Dynamic Client Registration + PKCE flow for MCP authorization.

---

## Overview: The Complete Flow in 8 Steps

```
┌─────────────┐                                                    ┌─────────────────┐
│             │                                                    │                 │
│  MCP Client │                                                    │   MCP Server    │
│  (AI Agent) │                                                    │  + OAuth Server │
│             │                                                    │                 │
└──────┬──────┘                                                    └────────┬────────┘
       │                                                                    │
       │ STEP 1: Discovery (Get Protected Resource Metadata)               │
       ├───────────────────────────────────────────────────────────────────►│
       │ GET /.well-known/oauth-protected-resource                         │
       │                                                                    │
       │◄───────────────────────────────────────────────────────────────────┤
       │ {                                                                  │
       │   "resource": "https://mcp.example.com",                           │
       │   "authorization_servers": ["https://mcp.example.com"],            │
       │   "scopes_supported": ["mcp:tools:read", "mcp:tools:execute"]      │
       │ }                                                                  │
       │                                                                    │
       │ STEP 2: Get Authorization Server Metadata                         │
       ├───────────────────────────────────────────────────────────────────►│
       │ GET /.well-known/oauth-authorization-server                       │
       │                                                                    │
       │◄───────────────────────────────────────────────────────────────────┤
       │ {                                                                  │
       │   "issuer": "https://mcp.example.com",                             │
       │   "authorization_endpoint": "https://mcp.example.com/oauth/authorize",│
       │   "token_endpoint": "https://mcp.example.com/oauth/token",         │
       │   "registration_endpoint": "https://mcp.example.com/oauth/register",│
       │   "code_challenge_methods_supported": ["S256"]                     │
       │ }                                                                  │
       │                                                                    │
       │ STEP 3: Dynamic Client Registration                               │
       ├───────────────────────────────────────────────────────────────────►│
       │ POST /oauth/register                                              │
       │ {                                                                  │
       │   "redirect_uris": ["http://localhost:8080/callback"],             │
       │   "client_name": "My AI Assistant"                                 │
       │ }                                                                  │
       │                                                                    │
       │◄───────────────────────────────────────────────────────────────────┤
       │ {                                                                  │
       │   "client_id": "client_abc123",                                    │
       │   "client_secret": "secret_xyz789",                                │
       │   "redirect_uris": ["http://localhost:8080/callback"]              │
       │ }                                                                  │
       │                                                                    │
       │ STEP 4: Generate PKCE Parameters (Client-Side)                    │
       │ code_verifier = random_string(43-128 chars)                        │
       │ code_challenge = base64url(sha256(code_verifier))                  │
       │                                                                    │
       │ STEP 5: Authorization Request                                     │
       ├───────────────────────────────────────────────────────────────────►│
       │ GET /oauth/authorize?                                             │
       │   response_type=code&                                              │
       │   client_id=client_abc123&                                         │
       │   redirect_uri=http://localhost:8080/callback&                     │
       │   scope=mcp:tools:read+mcp:tools:execute&                          │
       │   code_challenge=E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM&      │
       │   code_challenge_method=S256&                                      │
       │   state=random_state_123                                           │
       │                                                                    │
       │                    ┌──────────────────────────┐                    │
       │                    │  User Consent Screen     │                    │
       │                    │  (Auto-approved in mock) │                    │
       │                    └──────────────────────────┘                    │
       │                                                                    │
       │◄───────────────────────────────────────────────────────────────────┤
       │ HTTP 302 Redirect:                                                │
       │ Location: http://localhost:8080/callback?                          │
       │           code=AUTH_CODE_xyz&                                      │
       │           state=random_state_123                                   │
       │                                                                    │
       │ STEP 6: Token Exchange                                            │
       ├───────────────────────────────────────────────────────────────────►│
       │ POST /oauth/token                                                 │
       │ grant_type=authorization_code&                                     │
       │ code=AUTH_CODE_xyz&                                                │
       │ redirect_uri=http://localhost:8080/callback&                       │
       │ code_verifier=ORIGINAL_CODE_VERIFIER&                              │
       │ client_id=client_abc123                                            │
       │                                                                    │
       │            Server validates:                                       │
       │            - Code is valid and not expired                         │
       │            - Redirect URI matches                                  │
       │            - PKCE: sha256(code_verifier) == code_challenge         │
       │                                                                    │
       │◄───────────────────────────────────────────────────────────────────┤
       │ {                                                                  │
       │   "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",       │
       │   "token_type": "Bearer",                                          │
       │   "expires_in": 3600,                                              │
       │   "refresh_token": "refresh_abc123",                               │
       │   "scope": "mcp:tools:read mcp:tools:execute"                      │
       │ }                                                                  │
       │                                                                    │
       │ STEP 7: Call MCP Tool                                             │
       ├───────────────────────────────────────────────────────────────────►│
       │ POST /mcp/tools/call                                              │
       │ Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...      │
       │ {                                                                  │
       │   "jsonrpc": "2.0",                                                │
       │   "id": 1,                                                         │
       │   "method": "tools/call",                                          │
       │   "params": {                                                      │
       │     "name": "get_weather",                                         │
       │     "arguments": {"location": "San Francisco"}                     │
       │   }                                                                │
       │ }                                                                  │
       │                                                                    │
       │            Server validates JWT:                                   │
       │            - Signature valid                                       │
       │            - Not expired                                           │
       │            - Audience matches (if present)                         │
       │                                                                    │
       │◄───────────────────────────────────────────────────────────────────┤
       │ {                                                                  │
       │   "jsonrpc": "2.0",                                                │
       │   "id": 1,                                                         │
       │   "result": {                                                      │
       │     "temperature": 72,                                             │
       │     "conditions": "Sunny"                                          │
       │   }                                                                │
       │ }                                                                  │
       │                                                                    │
       │ STEP 8: Token Refresh (When Access Token Expires)                 │
       ├───────────────────────────────────────────────────────────────────►│
       │ POST /oauth/token                                                 │
       │ grant_type=refresh_token&                                          │
       │ refresh_token=refresh_abc123&                                      │
       │ client_id=client_abc123                                            │
       │                                                                    │
       │◄───────────────────────────────────────────────────────────────────┤
       │ {                                                                  │
       │   "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",       │
       │   "token_type": "Bearer",                                          │
       │   "expires_in": 3600,                                              │
       │   "refresh_token": "refresh_abc123",                               │
       │   "scope": "mcp:tools:read mcp:tools:execute"                      │
       │ }                                                                  │
       │                                                                    │
```

---

## Detailed Step-by-Step Breakdown

### Step 1: Discovery - Protected Resource Metadata

**Purpose**: Client learns which authorization server protects this MCP server

**Request**:
```http
GET /.well-known/oauth-protected-resource HTTP/1.1
Host: mcp.example.com
```

**Response** (RFC 9728):
```json
{
  "resource": "https://mcp.example.com",
  "authorization_servers": [
    "https://mcp.example.com"
  ],
  "scopes_supported": [
    "mcp:tools:read",
    "mcp:tools:execute"
  ],
  "bearer_methods_supported": ["header"]
}
```

**Key Information Learned**:
- 🔑 `authorization_servers`: Where to get tokens
- 🔑 `scopes_supported`: What permissions are available
- 🔑 `resource`: Canonical URI of this MCP server

**Implementation**: `server/app/oauth/metadata.py`

---

### Step 2: Authorization Server Metadata Discovery

**Purpose**: Learn about authorization server's capabilities and endpoints

**Request**:
```http
GET /.well-known/oauth-authorization-server HTTP/1.1
Host: mcp.example.com
```

**Response** (RFC 8414):
```json
{
  "issuer": "https://mcp.example.com",
  "authorization_endpoint": "https://mcp.example.com/oauth/authorize",
  "token_endpoint": "https://mcp.example.com/oauth/token",
  "registration_endpoint": "https://mcp.example.com/oauth/register",
  "response_types_supported": ["code"],
  "grant_types_supported": ["authorization_code", "refresh_token"],
  "code_challenge_methods_supported": ["S256"],
  "token_endpoint_auth_methods_supported": ["none", "client_secret_post"],
  "scopes_supported": ["mcp:tools:read", "mcp:tools:execute"]
}
```

**Key Information Learned**:
- 🔑 `registration_endpoint`: DCR is supported!
- 🔑 `authorization_endpoint`: Where to send users for consent
- 🔑 `token_endpoint`: Where to exchange codes for tokens
- 🔑 `code_challenge_methods_supported`: PKCE with S256 required

**Implementation**: `server/app/oauth/metadata.py`

---

### Step 3: Dynamic Client Registration (RFC 7591)

**Purpose**: Client self-registers to get `client_id` and `client_secret`

**Request**:
```http
POST /oauth/register HTTP/1.1
Host: mcp.example.com
Content-Type: application/json

{
  "redirect_uris": [
    "http://localhost:8080/callback"
  ],
  "client_name": "My AI Assistant",
  "grant_types": ["authorization_code", "refresh_token"],
  "response_types": ["code"],
  "token_endpoint_auth_method": "none"
}
```

**Response**:
```json
{
  "client_id": "client_d7f21a9c8b4e3f12",
  "client_secret": "secret_a1b2c3d4e5f6g7h8",
  "client_id_issued_at": 1699564800,
  "redirect_uris": [
    "http://localhost:8080/callback"
  ],
  "client_name": "My AI Assistant",
  "grant_types": ["authorization_code", "refresh_token"],
  "response_types": ["code"]
}
```

**What Happens Server-Side**:
1. Generate unique `client_id` (UUID-based)
2. Generate secure `client_secret` (32 random bytes)
3. Store client metadata in database
4. Return credentials to client

**Security Note**: Client must store `client_id` and `client_secret` securely!

**Implementation**: `server/app/oauth/dcr.py`

---

### Step 4: PKCE Parameter Generation (Client-Side)

**Purpose**: Generate cryptographic proof to prevent authorization code interception

**Code Verifier Generation**:
```python
import secrets
import base64

# Generate random 32-byte value
code_verifier = base64.urlsafe_b64encode(
    secrets.token_bytes(32)
).decode('utf-8').rstrip('=')

# Result: "dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk"
```

**Code Challenge Generation**:
```python
import hashlib

# SHA-256 hash of code verifier
digest = hashlib.sha256(code_verifier.encode('utf-8')).digest()

# Base64url encode
code_challenge = base64.urlsafe_b64encode(digest).decode('utf-8').rstrip('=')

# Result: "E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM"
```

**Critical**: Client MUST remember `code_verifier` for Step 6!

**Implementation**: `server/app/oauth/pkce.py`

---

### Step 5: Authorization Request

**Purpose**: Get user's permission to access their MCP tools

**Request**:
```http
GET /oauth/authorize?response_type=code&client_id=client_d7f21a9c8b4e3f12&redirect_uri=http%3A%2F%2Flocalhost%3A8080%2Fcallback&scope=mcp%3Atools%3Aread+mcp%3Atools%3Aexecute&code_challenge=E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM&code_challenge_method=S256&state=abc123xyz&resource=https%3A%2F%2Fmcp.example.com HTTP/1.1
Host: mcp.example.com
```

**Query Parameters Breakdown**:
| Parameter | Value | Purpose |
|-----------|-------|---------|
| `response_type` | `code` | Request authorization code |
| `client_id` | From Step 3 | Identify this client |
| `redirect_uri` | `http://localhost:8080/callback` | Where to send user after approval |
| `scope` | `mcp:tools:read mcp:tools:execute` | Permissions requested |
| `code_challenge` | From Step 4 | PKCE challenge |
| `code_challenge_method` | `S256` | SHA-256 hash algorithm |
| `state` | Random value | CSRF protection |
| `resource` | `https://mcp.example.com` | Target resource (RFC 8707) |

**User Sees**:
```
╔══════════════════════════════════════════════╗
║  Authorization Request                       ║
║                                              ║
║  My AI Assistant wants to:                   ║
║                                              ║
║  • Read your MCP tool list                   ║
║  • Execute tools on your behalf              ║
║                                              ║
║  [ Approve ]  [ Deny ]                       ║
╚══════════════════════════════════════════════╝
```

**Server Response** (after approval):
```http
HTTP/1.1 302 Found
Location: http://localhost:8080/callback?code=auth_code_xyz789&state=abc123xyz
```

**What Happens Server-Side**:
1. Validate `client_id` is registered
2. Validate `redirect_uri` matches registration
3. Validate `code_challenge_method` is supported (S256)
4. Show consent screen (auto-approved in mock server)
5. Generate single-use authorization code
6. Store: `{ code, client_id, user_id, redirect_uri, code_challenge, scope, expires_at }`
7. Redirect user to `redirect_uri` with code

**Implementation**: `server/app/oauth/authorize.py`

---

### Step 6: Token Exchange

**Purpose**: Exchange authorization code + PKCE proof for access token

**Request**:
```http
POST /oauth/token HTTP/1.1
Host: mcp.example.com
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code&
code=auth_code_xyz789&
redirect_uri=http%3A%2F%2Flocalhost%3A8080%2Fcallback&
code_verifier=dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk&
client_id=client_d7f21a9c8b4e3f12
```

**Server Validation**:
1. ✅ Authorization code exists and not expired
2. ✅ `client_id` matches code's client
3. ✅ `redirect_uri` matches exactly
4. ✅ **PKCE Verification**: `sha256(code_verifier) == stored_code_challenge`
5. ✅ Mark code as used (prevent replay)

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyXzEyMyIsImNsaWVudF9pZCI6ImNsaWVudF9kN2YyMWE5YzhiNGUzZjEyIiwic2NvcGUiOiJtY3A6dG9vbHM6cmVhZCBtY3A6dG9vbHM6ZXhlY3V0ZSIsImV4cCI6MTY5OTU2ODQwMCwiaWF0IjoxNjk5NTY0ODAwLCJpc3MiOiJodHRwczovL21jcC5leGFtcGxlLmNvbSJ9.signature",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "refresh_abc123def456",
  "scope": "mcp:tools:read mcp:tools:execute"
}
```

**Access Token (JWT) Claims**:
```json
{
  "sub": "user_123",
  "client_id": "client_d7f21a9c8b4e3f12",
  "scope": "mcp:tools:read mcp:tools:execute",
  "exp": 1699568400,
  "iat": 1699564800,
  "iss": "https://mcp.example.com",
  "aud": "https://mcp.example.com"
}
```

**Implementation**: `server/app/oauth/token.py`

---

### Step 7: Authenticated MCP Tool Call

**Purpose**: Execute MCP tool with user's authorized access

**Request**:
```http
POST /mcp/tools/call HTTP/1.1
Host: mcp.example.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "get_weather",
    "arguments": {
      "location": "San Francisco, CA",
      "units": "fahrenheit"
    }
  }
}
```

**Server Validation**:
1. ✅ Extract Bearer token from `Authorization` header
2. ✅ Verify JWT signature
3. ✅ Check token not expired (`exp` claim)
4. ✅ Validate audience (`aud` claim matches server)
5. ✅ Check scope includes `mcp:tools:execute`
6. ✅ Extract `user_id` from `sub` claim
7. ✅ Execute tool with user context

**Response**:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "location": "San Francisco, CA",
    "temperature": 72,
    "units": "fahrenheit",
    "conditions": "Sunny",
    "timestamp": "2025-11-03T15:30:00Z"
  }
}
```

**Error Response** (if token invalid):
```http
HTTP/1.1 401 Unauthorized
WWW-Authenticate: Bearer realm="mcp-server",
                  as_uri="https://mcp.example.com/.well-known/oauth-authorization-server",
                  resource="https://mcp.example.com"
Content-Type: application/json

{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32600,
    "message": "Invalid or expired access token"
  }
}
```

**Implementation**: `server/app/mcp/protocol.py`

---

### Step 8: Token Refresh

**Purpose**: Get new access token when current one expires

**Request**:
```http
POST /oauth/token HTTP/1.1
Host: mcp.example.com
Content-Type: application/x-www-form-urlencoded

grant_type=refresh_token&
refresh_token=refresh_abc123def456&
client_id=client_d7f21a9c8b4e3f12
```

**Server Validation**:
1. ✅ Refresh token exists and not expired
2. ✅ Refresh token not revoked
3. ✅ `client_id` matches token's client

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "refresh_abc123def456",
  "scope": "mcp:tools:read mcp:tools:execute"
}
```

**Note**: In this implementation, refresh token is reused. OAuth 2.1 recommends **refresh token rotation** for public clients (issuing new refresh token each time).

**Implementation**: `server/app/oauth/token.py`

---

## Security Properties Enforced

### PKCE (Proof Key for Code Exchange)

**Threat**: Authorization code interception attack
- Attacker intercepts authorization code during redirect
- Attacker tries to exchange code for tokens

**Mitigation**:
- Client generates secret `code_verifier` (never transmitted)
- Client sends `code_challenge = sha256(code_verifier)` in Step 5
- Server stores `code_challenge` with authorization code
- Client proves ownership by providing `code_verifier` in Step 6
- Server verifies: `sha256(received_code_verifier) == stored_code_challenge`
- ✅ Attacker cannot forge `code_verifier` without breaking SHA-256

### Single-Use Authorization Codes

**Threat**: Code replay attack
- Attacker steals authorization code
- Attacker tries to exchange it multiple times

**Mitigation**:
- Server marks code as "used" after successful token exchange
- Subsequent attempts with same code are rejected
- Codes expire after 10 minutes (configurable)

### Redirect URI Validation

**Threat**: Open redirect attack
- Attacker manipulates `redirect_uri` to steal authorization code

**Mitigation**:
- Client registers exact redirect URIs during DCR (Step 3)
- Server validates `redirect_uri` in Step 5 matches registration (exact match)
- Server validates `redirect_uri` in Step 6 matches Step 5
- No wildcards or partial matches allowed

### State Parameter

**Threat**: CSRF attack on callback endpoint
- Attacker tricks user into authorizing attacker's client

**Mitigation**:
- Client generates random `state` parameter in Step 5
- Server echoes `state` in redirect (Step 5)
- Client verifies `state` matches original value
- Prevents cross-site request forgery

---

## JWT Token Structure

### Access Token Anatomy

**Header**:
```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

**Payload (Claims)**:
```json
{
  "sub": "user_123",              // Subject (user ID)
  "client_id": "client_abc123",   // Client that requested token
  "scope": "mcp:tools:read mcp:tools:execute",
  "exp": 1699568400,              // Expiration time (Unix timestamp)
  "iat": 1699564800,              // Issued at
  "iss": "https://mcp.example.com", // Issuer
  "aud": "https://mcp.example.com"  // Audience (⚠️ currently missing in implementation)
}
```

**Signature**:
```
HMACSHA256(
  base64UrlEncode(header) + "." + base64UrlEncode(payload),
  secret_key
)
```

**Validation**:
1. Verify signature using server's secret key
2. Check `exp` (expiration) is in the future
3. Check `aud` (audience) matches this server
4. Check `iss` (issuer) is trusted

---

## Error Scenarios

### Invalid Client Credentials

**Request**: Token exchange with wrong `client_id`

**Response**:
```http
HTTP/1.1 401 Unauthorized
Content-Type: application/json

{
  "error": "invalid_client",
  "error_description": "Invalid client credentials"
}
```

### Expired Authorization Code

**Request**: Token exchange with code older than 10 minutes

**Response**:
```http
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
  "error": "invalid_grant",
  "error_description": "Invalid or expired authorization code"
}
```

### PKCE Verification Failure

**Request**: Token exchange with wrong `code_verifier`

**Response**:
```http
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
  "error": "invalid_grant",
  "error_description": "Invalid code_verifier"
}
```

### Expired Access Token

**Request**: MCP tool call with expired JWT

**Response**:
```http
HTTP/1.1 401 Unauthorized
WWW-Authenticate: Bearer realm="mcp-server",
                  as_uri="https://mcp.example.com/.well-known/oauth-authorization-server",
                  resource="https://mcp.example.com"
Content-Type: application/json

{
  "detail": "Invalid token: Signature has expired"
}
```

**Client Action**: Use refresh token (Step 8) to get new access token

---

## Implementation Notes

### Co-Located Authorization Server

In this implementation, the OAuth authorization server and MCP resource server are the **same application**. This simplifies deployment but has trade-offs:

**Advantages**:
- Single deployment unit
- No network latency between auth and resource server
- MCP-aware authorization logic
- Simpler token validation (shared secret key)

**Disadvantages**:
- Can't reuse auth server for multiple resource servers
- Harder to separate security concerns
- Scaling auth and resources independently requires code changes

**Production Alternative**: Use separate authorization server (e.g., Keycloak, Auth0, Okta) and implement token introspection endpoint.

### Token Validation Strategy

**Current (JWT)**:
- Stateless validation
- No database lookup on every request
- Faster for high-traffic scenarios
- Cannot revoke tokens before expiration

**Alternative (Opaque Tokens)**:
- Database lookup on every request
- Can revoke tokens immediately
- Slower but more flexible
- Better for sensitive operations

---

## Testing the Flow

See `server/tests/test_flow.py` for complete end-to-end test:

```bash
cd server
python tests/test_flow.py
```

**Test Output**:
```
✅ Step 1: Client Registration Successful
   client_id: client_abc123...

✅ Step 2: PKCE Parameters Generated
   code_challenge: E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM

✅ Step 3: Authorization Code Obtained
   code: auth_xyz789...

✅ Step 4: Tokens Acquired
   access_token: eyJhbGci...
   refresh_token: refresh_abc...

✅ Step 5: Tool Listing Successful
   Available tools: get_weather, list_files, get_user_profile

✅ Step 6: Tool Execution Successful
   Result: {"temperature": 72, "conditions": "Sunny"}

✅ Step 7: Token Refresh Successful
   New access_token: eyJhbGci...

All tests passed! ✅
```

---

## Further Reading

- **[RFC 7591](https://datatracker.ietf.org/doc/html/rfc7591)** - Dynamic Client Registration Protocol
- **[RFC 7636](https://datatracker.ietf.org/doc/html/rfc7636)** - Proof Key for Code Exchange (PKCE)
- **[RFC 8414](https://datatracker.ietf.org/doc/html/rfc8414)** - Authorization Server Metadata
- **[RFC 9728](https://datatracker.ietf.org/doc/html/rfc9728)** - Protected Resource Metadata
- **[MCP Authorization Spec](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization)** - MCP-specific auth requirements

---

**Next Steps**: See [security/](security/) for comprehensive security audits and [ARCHITECTURE.md](ARCHITECTURE.md) for design rationale.
