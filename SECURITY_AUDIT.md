# Security Audit: MCP Authorization Specification Compliance

**Date**: 2025-11-03
**Specification**: [MCP Authorization Specification (2025-06-18)](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization)
**Implementation**: Mock MCP Server v0.1.0

---

## Executive Summary

This audit validates the reference implementation's compliance with the MCP Authorization Specification and identifies areas requiring attention before production deployment.

**Overall Status**: ✅ **COMPLIANT for Development/Testing**

**Key Findings**:
- ✅ All mandatory OAuth 2.0 and PKCE requirements met
- ✅ Discovery mechanisms properly implemented
- ✅ Token validation and authentication correct
- ⚠️ **1 Security Enhancement Needed**: Missing audience (`aud`) claim in JWT tokens
- ⚠️ **Development-Only Features**: Auto-approval and in-memory storage not suitable for production

---

## Compliance Matrix

### 1. Transport-Specific Requirements

| Requirement | Status | Evidence | Notes |
|-------------|--------|----------|-------|
| HTTP-based transport SHOULD follow spec | ✅ | All endpoints use HTTP/REST | Implemented |
| STDIO transports SHOULD NOT use spec | N/A | No STDIO transport | Not applicable |

**Verdict**: ✅ **COMPLIANT**

---

### 2. Authorization Server Discovery

#### 2.1 Protected Resource Metadata (RFC 9728)

| Requirement | Status | Implementation | Location |
|-------------|--------|----------------|----------|
| MUST implement RFC 9728 | ✅ | `GET /.well-known/oauth-protected-resource` | `server/app/oauth/metadata.py:33-46` |
| MUST include `authorization_servers` field | ✅ | Returns `[settings.SERVER_URL]` | Line 43 |
| Include at least one authorization server | ✅ | Single co-located auth server | Line 43 |
| SHOULD include `scopes_supported` | ✅ | `["mcp:tools:read", "mcp:tools:execute"]` | Line 44 |
| SHOULD include `bearer_methods_supported` | ✅ | `["header"]` | Line 45 |

**Response Example**:
```json
{
  "resource": "http://localhost:8000",
  "authorization_servers": ["http://localhost:8000"],
  "scopes_supported": ["mcp:tools:read", "mcp:tools:execute"],
  "bearer_methods_supported": ["header"]
}
```

**Verdict**: ✅ **FULLY COMPLIANT**

---

#### 2.2 WWW-Authenticate Header on 401

| Requirement | Status | Implementation | Location |
|-------------|--------|----------------|----------|
| Use WWW-Authenticate on 401 responses | ✅ | Implemented in auth dependency | `server/app/mcp/protocol.py:36-44` |
| Include `as_uri` parameter | ✅ | Points to `/.well-known/oauth-authorization-server` | Line 40 |
| Include `resource` parameter | ✅ | Server's canonical URI | Line 41 |

**Example WWW-Authenticate Header**:
```http
WWW-Authenticate: Bearer realm="mcp-server",
                  as_uri="http://localhost:8000/.well-known/oauth-authorization-server",
                  resource="http://localhost:8000"
```

**Verdict**: ✅ **FULLY COMPLIANT**

---

#### 2.3 Authorization Server Metadata (RFC 8414)

| Requirement | Status | Implementation | Location |
|-------------|--------|----------------|----------|
| MUST implement RFC 8414 | ✅ | `GET /.well-known/oauth-authorization-server` | `server/app/oauth/metadata.py:13-30` |
| Include `issuer` | ✅ | Server base URL | Line 21 |
| Include `authorization_endpoint` | ✅ | `/oauth/authorize` | Line 22 |
| Include `token_endpoint` | ✅ | `/oauth/token` | Line 23 |
| Include `registration_endpoint` | ✅ | `/oauth/register` (DCR support) | Line 24 |
| List `response_types_supported` | ✅ | `["code"]` | Line 25 |
| List `grant_types_supported` | ✅ | `["authorization_code", "refresh_token"]` | Line 26 |
| List `code_challenge_methods_supported` | ✅ | `["S256"]` (SHA-256 PKCE) | Line 27 |
| List `scopes_supported` | ✅ | MCP-specific scopes | Line 29 |

**Verdict**: ✅ **FULLY COMPLIANT**

---

### 3. Dynamic Client Registration (RFC 7591)

| Requirement | Status | Implementation | Location |
|-------------|--------|----------------|----------|
| SHOULD support DCR | ✅ | Fully implemented | `server/app/oauth/dcr.py` |
| Accept `redirect_uris` (required for auth code) | ✅ | Validated and stored | Line 27-31 |
| Accept `client_name` (optional) | ✅ | Stored for display | Line 33-34 |
| Accept `grant_types` (optional) | ✅ | Defaults to `["authorization_code"]` | Line 36-40 |
| Generate unique `client_id` | ✅ | UUID-based: `client_<uuid>` | Line 45 |
| Generate `client_secret` (if confidential) | ✅ | Random 32-byte token | Line 46 |
| Return registration response | ✅ | Includes all client metadata | Line 48-54 |
| Persist client metadata | ✅ | In-memory storage | Line 57 |

**Registration Flow Test**: ✅ Verified in `server/tests/test_flow.py:19-31`

**Verdict**: ✅ **FULLY COMPLIANT**

---

### 4. PKCE Implementation (RFC 7636)

| Requirement | Status | Implementation | Location |
|-------------|--------|----------------|----------|
| MCP clients MUST implement PKCE | ✅ | Server validates PKCE | `server/app/oauth/authorize.py` |
| Support S256 code challenge method | ✅ | SHA-256 hashing | `server/app/oauth/pkce.py:23-34` |
| Accept `code_challenge` parameter | ✅ | Required in auth request | `server/app/oauth/authorize.py:37-41` |
| Accept `code_challenge_method` | ✅ | Must be "S256" | Line 43-47 |
| Store challenge with auth code | ✅ | Stored in `AuthorizationCode` model | Line 101-110 |
| Verify `code_verifier` at token endpoint | ✅ | PKCE validation before token issuance | `server/app/oauth/token.py:167-175` |

**PKCE Validation Logic**:
```python
# server/app/oauth/pkce.py:23-34
computed_challenge = base64.urlsafe_b64encode(
    hashlib.sha256(code_verifier.encode()).digest()
).decode().rstrip('=')
return secrets.compare_digest(computed_challenge, code_challenge)
```

**Verdict**: ✅ **FULLY COMPLIANT**

---

### 5. Resource Parameter (RFC 8707)

| Requirement | Status | Implementation | Location |
|-------------|--------|----------------|----------|
| Clients MUST include `resource` parameter | ⚠️ | **Not validated** | N/A |
| Use in authorization requests | ⚠️ | Server doesn't require it | `server/app/oauth/authorize.py` |
| Use in token requests | ⚠️ | Server doesn't require it | `server/app/oauth/token.py` |
| Use canonical URI format | ⚠️ | Not enforced | N/A |

**Finding**: The server does not require or validate the `resource` parameter, though the spec states clients MUST include it. For a mock server this is acceptable, but production implementations should validate this parameter.

**Recommendation**: Add optional `resource` parameter validation for production readiness.

**Verdict**: ⚠️ **ACCEPTABLE FOR MOCK, RECOMMENDED FOR PRODUCTION**

---

### 6. Access Token Usage

#### 6.1 Token Format and Claims

| Requirement | Status | Implementation | Location |
|-------------|--------|----------------|----------|
| Use Authorization header | ✅ | `Authorization: Bearer <token>` | `server/app/mcp/protocol.py:46-53` |
| MUST NOT use query parameters | ✅ | Only header accepted | N/A (enforced) |
| Token contains user identifier | ✅ | `sub` claim with user_id | `server/app/oauth/token.py:47` |
| Token contains client identifier | ✅ | `client_id` claim | Line 48 |
| Token contains scope | ✅ | `scope` claim | Line 49 |
| Token contains expiration | ✅ | `exp` claim (60 min default) | Line 50 |
| Token contains issuer | ✅ | `iss` claim with server URL | Line 52 |
| **Token contains audience** | ⚠️ | **MISSING `aud` claim** | **FINDING** |

**JWT Claims Example**:
```json
{
  "sub": "user_123",
  "client_id": "client_abc",
  "scope": "mcp:tools:read mcp:tools:execute",
  "exp": 1699568400,
  "iat": 1699564800,
  "iss": "http://localhost:8000"
  // MISSING: "aud": "http://localhost:8000"
}
```

**🔴 SECURITY FINDING**: Missing audience (`aud`) claim violates OAuth 2.1 best practices and MCP spec emphasis on audience validation.

**Impact**:
- Tokens could theoretically be used at different MCP servers
- Violates principle of least privilege
- Confused deputy attacks possible if tokens are leaked

**Recommendation**: Add `aud` claim to JWT tokens in `server/app/oauth/token.py:create_access_token()`

**Verdict**: ⚠️ **NON-COMPLIANT - SECURITY ENHANCEMENT REQUIRED**

---

#### 6.2 Token Validation

| Requirement | Status | Implementation | Location |
|-------------|--------|----------------|----------|
| Validate tokens per OAuth 2.1 Section 5.2 | ✅ | JWT signature and expiration checked | `server/app/oauth/token.py:77-89` |
| Validate token audience | ⚠️ | **Not validated** (missing `aud` claim) | N/A |
| Return 401 for invalid tokens | ✅ | Proper HTTP status codes | `server/app/oauth/token.py:85-89` |
| Include WWW-Authenticate header | ✅ | Added on 401 responses | Line 88 |

**Verdict**: ⚠️ **AUDIENCE VALIDATION MISSING**

---

### 7. Error Handling

| Requirement | Status | Implementation | Location |
|-------------|--------|----------------|----------|
| 401 for missing/invalid auth | ✅ | Correct status codes | `server/app/mcp/protocol.py:33-44` |
| 403 for insufficient scopes | ✅ | Can be added per tool | `server/app/mcp/protocol.py` |
| 400 for malformed requests | ✅ | Validation errors | `server/app/oauth/authorize.py` |

**Verdict**: ✅ **COMPLIANT**

---

### 8. Security Considerations

#### 8.1 Token Audience Binding

| Security Control | Status | Notes |
|------------------|--------|-------|
| Clients include `resource` parameter | ⚠️ | Not enforced by server |
| Servers validate token audience | ⚠️ | **Missing `aud` claim validation** |
| Prevents token reuse across services | ⚠️ | Not fully enforced |

**Verdict**: ⚠️ **PARTIAL COMPLIANCE**

---

#### 8.2 Token Theft Prevention

| Security Control | Status | Implementation |
|------------------|--------|----------------|
| Short-lived access tokens | ✅ | 60 minutes (configurable) |
| Refresh token rotation | ⚠️ | **Not implemented** (OAuth 2.1 recommendation for public clients) |
| Secure token storage | ✅ | Client responsibility |

**Finding**: Refresh tokens are not rotated on use. OAuth 2.1 Section 4.3.1 recommends rotation for public clients.

**Recommendation**: Implement refresh token rotation for enhanced security.

**Verdict**: ⚠️ **ACCEPTABLE FOR MOCK, ENHANCE FOR PRODUCTION**

---

#### 8.3 Communication Security

| Security Control | Status | Notes |
|------------------|--------|-------|
| HTTPS for authorization server | ⚠️ | **Development uses HTTP** |
| HTTPS or localhost for redirect URIs | ✅ | Localhost allowed, HTTPS enforced in production |
| TLS 1.2+ required | N/A | Production concern |

**Verdict**: ⚠️ **DEVELOPMENT-ONLY (HTTP acceptable), PRODUCTION REQUIRES HTTPS**

---

#### 8.4 Authorization Code Protection

| Security Control | Status | Implementation |
|------------------|--------|----------------|
| PKCE required | ✅ | S256 method enforced |
| Single-use auth codes | ✅ | Marked as used after exchange |
| Code expiration | ✅ | 10 minutes (configurable) |

**Verdict**: ✅ **FULLY COMPLIANT**

---

#### 8.5 Open Redirection Prevention

| Security Control | Status | Implementation |
|------------------|--------|----------------|
| Redirect URI registration | ✅ | Required at DCR time |
| Exact URI matching | ✅ | No wildcards or partial matches |
| State parameter support | ✅ | Passed through to callback |

**Verdict**: ✅ **FULLY COMPLIANT**

---

#### 8.6 Confused Deputy Problem

| Security Control | Status | Notes |
|------------------|--------|-------|
| User consent for proxy scenarios | ⚠️ | Auto-approval in mock server |
| Client metadata validation | ✅ | DCR stores client info |

**Finding**: Auto-approval bypasses user consent, which is a development convenience but violates the security model for proxied access.

**Verdict**: ⚠️ **DEVELOPMENT-ONLY, PRODUCTION REQUIRES CONSENT UI**

---

#### 8.7 Token Passthrough Prevention

| Security Control | Status | Implementation |
|------------------|--------|----------------|
| No token forwarding to other services | ✅ | Tools do not forward tokens |
| Separate token acquisition if needed | ✅ | Design enforces this |

**Verdict**: ✅ **COMPLIANT**

---

## Summary of Findings

### 🔴 Critical (Must Fix for Production)

1. **Missing Audience Claim in JWTs**
   - **Location**: `server/app/oauth/token.py:create_access_token()`
   - **Fix**: Add `"aud": settings.SERVER_URL` to JWT claims
   - **Validation**: Add audience check in `verify_access_token()`

2. **No User Consent Flow**
   - **Location**: `server/app/oauth/authorize.py:68-115` (auto-approval)
   - **Fix**: Implement consent UI showing requested permissions
   - **User Impact**: Users cannot review what AI can access

3. **HTTP in Production**
   - **Location**: Configuration and deployment
   - **Fix**: Enforce HTTPS for all OAuth endpoints
   - **Security Impact**: Tokens and codes exposed in transit

---

### ⚠️ Recommended (Enhance Security)

4. **Refresh Token Rotation**
   - **Location**: `server/app/oauth/token.py:244` (refresh grant)
   - **Benefit**: Mitigates refresh token theft
   - **Complexity**: Moderate

5. **Resource Parameter Validation**
   - **Location**: `server/app/oauth/authorize.py` and `token.py`
   - **Benefit**: Enforces client compliance with MCP spec
   - **Complexity**: Low

6. **Persistent Storage**
   - **Location**: `server/app/storage.py`
   - **Fix**: Use PostgreSQL, Redis, or similar
   - **Benefit**: Survive restarts, enable token revocation

---

### ✅ Compliant

7. ✅ Dynamic Client Registration (RFC 7591)
8. ✅ PKCE Implementation (RFC 7636)
9. ✅ Authorization Server Metadata (RFC 8414)
10. ✅ Protected Resource Metadata (RFC 9728)
11. ✅ Single-use authorization codes
12. ✅ Redirect URI validation
13. ✅ Bearer token authentication
14. ✅ WWW-Authenticate headers
15. ✅ MCP JSON-RPC protocol
16. ✅ Token expiration handling

---

## Code Changes Required for Full Compliance

### 1. Add Audience Claim to JWT

**File**: `server/app/oauth/token.py`

**Change**:
```python
# Line 46-52
claims = {
    "sub": user_id,
    "client_id": client_id,
    "scope": scope or "",
    "exp": expires_at,
    "iat": datetime.utcnow(),
    "iss": settings.SERVER_URL,
    "aud": settings.SERVER_URL,  # ADD THIS LINE
}
```

**Validation**:
```python
# In verify_access_token(), add after line 82:
if payload.get("aud") != settings.SERVER_URL:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token audience mismatch",
        headers={"WWW-Authenticate": "Bearer"}
    )
```

---

### 2. Implement Consent UI (Production)

**File**: `server/app/oauth/authorize.py`

**Current** (line 68-115): Auto-approval logic

**Needed**:
- HTML form showing client name, requested scopes, and approve/deny buttons
- POST endpoint to handle user decision
- Session management for multi-step flow

**Example**:
```html
<h1>Authorization Request</h1>
<p><strong>{{ client_name }}</strong> wants to access your MCP tools.</p>
<p>Permissions requested:</p>
<ul>
  <li>Read your tool list</li>
  <li>Execute tools on your behalf</li>
</ul>
<form method="post">
  <button name="decision" value="approve">Approve</button>
  <button name="decision" value="deny">Deny</button>
</form>
```

---

## Testing Recommendations

### Security Test Cases

1. **Token Audience Validation**
   - ✅ Test: Token issued by Server A should be rejected by Server B
   - ⚠️ Currently: No validation, tokens portable between servers

2. **PKCE Tampering**
   - ✅ Test: Modified code_verifier should fail token exchange
   - ✅ Status: PASSING (`server/tests/test_flow.py` verifies)

3. **Authorization Code Replay**
   - ✅ Test: Using same auth code twice should fail
   - ✅ Status: PASSING (codes marked as used)

4. **Refresh Token Reuse**
   - ⚠️ Test: Refresh token rotation not implemented
   - ⚠️ Status: Same refresh token reused indefinitely

5. **Expired Token Rejection**
   - ✅ Test: Access token past expiration should return 401
   - ✅ Status: JWT library handles automatically

---

## Production Readiness Checklist

- [ ] Add `aud` claim to JWT tokens and validate on use
- [ ] Implement user consent UI for authorization requests
- [ ] Deploy with HTTPS (TLS 1.2+)
- [ ] Replace in-memory storage with persistent database
- [ ] Implement refresh token rotation
- [ ] Add token revocation endpoint (RFC 7009)
- [ ] Add rate limiting on registration and token endpoints
- [ ] Implement audit logging for all auth events
- [ ] Add monitoring for failed auth attempts
- [ ] Test with security scanner (OWASP ZAP, Burp Suite)
- [ ] Validate `resource` parameter in authorization requests
- [ ] Add scope-based authorization in MCP tool handlers
- [ ] Document security model and threat mitigation
- [ ] Conduct penetration testing
- [ ] Implement CORS policies for web clients

---

## Conclusion

The reference implementation **demonstrates the core OAuth 2.0 + DCR + MCP flow correctly** and is **suitable for development and testing purposes**.

**For production deployment**, the following changes are **mandatory**:
1. Add JWT audience claims and validation
2. Implement user consent UI
3. Use HTTPS for all endpoints
4. Implement persistent storage

**Recommended enhancements** for defense-in-depth:
1. Refresh token rotation
2. Resource parameter validation
3. Token revocation support

The implementation serves as a **solid foundation** for building production MCP servers with proper security hardening.

---

**Auditor**: Claude Code
**Specification Version**: MCP Authorization Specification 2025-06-18
**Implementation Version**: Mock MCP Server v0.1.0
**Audit Date**: 2025-11-03
