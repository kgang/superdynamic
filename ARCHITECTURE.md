# Architecture: MCP with OAuth 2.0 and Dynamic Client Registration

## Executive Summary

This document synthesizes the **conceptual foundation** and **architectural decisions** behind implementing OAuth 2.0 Dynamic Client Registration (DCR) with the Model Context Protocol (MCP). It answers the fundamental questions: *Why does this matter?* and *When should you use this approach?*

---

## The Problem: MCP in Enterprise Environments

### Traditional MCP Limitations

Model Context Protocol (MCP) enables AI applications to interact with external tools and data sources through a standardized interface. However, the base MCP specification doesn't address a critical enterprise need: **secure, user-authorized access to protected resources**.

Traditional approaches face challenges:
- **Hard-coded credentials**: Embedding API keys or tokens in configurations is insecure and doesn't scale
- **Single-user systems**: Can't distinguish between different users accessing the same MCP server
- **Manual setup friction**: Each client-server pairing requires manual configuration
- **No consent flow**: Users can't review or approve what data the AI can access

### The Enterprise Reality

Real-world enterprise tools require:
1. **User identity**: Which user is the AI acting on behalf of?
2. **Delegated authorization**: What permissions has the user granted?
3. **Audit trails**: Who accessed what data, when?
4. **Dynamic onboarding**: New integrations shouldn't require IT intervention

---

## The Solution: OAuth 2.0 + DCR + MCP

### Why OAuth 2.0?

OAuth 2.0 is the industry-standard protocol for **delegated authorization**. It allows users to grant limited access to their resources without sharing credentials.

**Key OAuth 2.0 Benefits:**
- **Separation of concerns**: Authorization server handles auth, resource server handles data
- **Scoped permissions**: Fine-grained control over what clients can access
- **Token-based security**: Short-lived access tokens, long-lived refresh tokens
- **Proven at scale**: Used by Google, Microsoft, GitHub, and thousands of enterprise APIs

### Why Dynamic Client Registration (RFC 7591)?

Traditional OAuth requires **pre-registration**: A developer manually registers their app with each service provider to get a `client_id` and `client_secret`. This doesn't work for AI agents that need to connect to arbitrary MCP servers on the fly.

**DCR enables:**
- **Zero-touch onboarding**: Client automatically registers when connecting to a new server
- **No pre-shared secrets**: Registration happens programmatically
- **Metadata exchange**: Client and server negotiate capabilities automatically
- **Scalability**: One AI agent can connect to hundreds of MCP servers without manual setup

### Why PKCE (RFC 7636)?

Proof Key for Code Exchange (PKCE) protects the authorization code flow from interception attacks, especially critical for:
- **Public clients**: Desktop apps, CLI tools, and mobile apps that can't securely store client secrets
- **Local callback servers**: Redirect URIs like `http://localhost:3000/callback` are vulnerable to port hijacking
- **Code injection attacks**: Attackers could steal authorization codes in transit

**PKCE adds:**
- **Code challenge**: Client commits to a random value before starting OAuth flow
- **Code verifier**: Client proves ownership of the challenge when exchanging the code
- **No client secret needed**: Suitable for CLI tools and native applications

---

## How It All Fits Together

### The Complete Flow

```
┌─────────────┐                                           ┌──────────────────┐
│             │  1. Discover metadata                     │   MCP Server     │
│             │ ────────────────────────────────────────► │  (Protected      │
│             │  /.well-known/oauth-protected-resource    │   Resource)      │
│             │                                           │                  │
│             │  2. Get auth server metadata              └────────┬─────────┘
│   MCP       │ ──────────────────────────┐                       │
│   Client    │                           │                       │
│             │                           ▼                       │
│             │         ┌──────────────────────────────┐          │
│             │  3. DCR │  OAuth 2.0 Authorization     │          │
│             │ ───────►│  Server                      │          │
│             │         │                              │          │
│             │  4. Get │  - Issues client_id          │          │
│             │    auth │  - Validates PKCE            │          │
│             │    code │  - Issues tokens             │          │
│             │ ───────►│                              │          │
│             │         └──────────────────────────────┘          │
│             │  5. Exchange code for token                       │
│             │ ───────►                                          │
│             │                                                   │
│             │  6. Call MCP tool with Bearer token               │
│             │ ──────────────────────────────────────────────────►
│             │         Authorization: Bearer <jwt>               │
└─────────────┘
```

### Step-by-Step Breakdown

#### Phase 1: Discovery
1. **Client discovers resource metadata** (`GET /.well-known/oauth-protected-resource`)
   - Server reveals which authorization servers it trusts
   - Server advertises required scopes (e.g., `mcp:tools:read`, `mcp:tools:execute`)

2. **Client fetches authorization server metadata** (`GET /.well-known/oauth-authorization-server`)
   - Discovers endpoints: registration, authorization, token
   - Learns supported features: grant types, PKCE methods, scopes

#### Phase 2: Dynamic Client Registration
3. **Client registers itself** (`POST /oauth/register`)
   ```json
   REQUEST:
   {
     "redirect_uris": ["http://localhost:8080/callback"],
     "client_name": "AI Assistant MCP Client",
     "grant_types": ["authorization_code", "refresh_token"]
   }

   RESPONSE:
   {
     "client_id": "mcp_client_abc123",
     "client_secret": "secret_xyz789",  // Optional for public clients
     "redirect_uris": ["http://localhost:8080/callback"],
     "client_id_issued_at": 1699564800
   }
   ```

#### Phase 3: User Authorization (OAuth + PKCE)
4. **Client generates PKCE parameters**
   ```python
   code_verifier = random_string(43-128 chars)
   code_challenge = base64url(sha256(code_verifier))
   ```

5. **Client initiates authorization** (`GET /oauth/authorize`)
   ```
   GET /oauth/authorize?
     response_type=code&
     client_id=mcp_client_abc123&
     redirect_uri=http://localhost:8080/callback&
     scope=mcp:tools:read+mcp:tools:execute&
     code_challenge=E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM&
     code_challenge_method=S256&
     state=random_state_123
   ```

   - User sees consent screen: "AI Assistant wants to access your MCP tools"
   - User approves
   - Server redirects: `http://localhost:8080/callback?code=AUTH_CODE&state=random_state_123`

6. **Client exchanges code for tokens** (`POST /oauth/token`)
   ```
   POST /oauth/token
   Content-Type: application/x-www-form-urlencoded

   grant_type=authorization_code&
   code=AUTH_CODE&
   redirect_uri=http://localhost:8080/callback&
   code_verifier=ORIGINAL_CODE_VERIFIER&
   client_id=mcp_client_abc123
   ```

   Response:
   ```json
   {
     "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
     "token_type": "Bearer",
     "expires_in": 3600,
     "refresh_token": "refresh_token_abc123",
     "scope": "mcp:tools:read mcp:tools:execute"
   }
   ```

#### Phase 4: MCP Tool Invocation
7. **Client calls MCP tool with access token**
   ```json
   POST /mcp/tools/call
   Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

   {
     "jsonrpc": "2.0",
     "id": 1,
     "method": "tools/call",
     "params": {
       "name": "get_user_profile",
       "arguments": {}
     }
   }
   ```

8. **Server validates token and executes tool**
   - Verifies JWT signature
   - Checks token expiration
   - Validates audience (token issued for this server)
   - Extracts user ID from token claims
   - Executes tool with user context
   - Returns result

---

## Key Architectural Decisions

### 1. Co-located Authorization Server

**Decision**: Implement authorization server as part of the MCP server

**Rationale**:
- **Simplicity**: Single deployment unit for development and testing
- **MCP-aware**: Authorization server understands MCP scopes and semantics
- **Lower latency**: No network hops between resource server and auth server

**Trade-offs**:
- In production, separating these concerns allows:
  - Centralized auth server for multiple resource servers
  - Specialized security hardening of auth components
  - Independent scaling

### 2. JWT Access Tokens

**Decision**: Use self-contained JWT tokens instead of opaque tokens

**Rationale**:
- **Stateless validation**: Server doesn't need to query database on every request
- **Contains user context**: Token includes `user_id`, `client_id`, `scope` claims
- **Standard format**: Industry-standard with libraries in every language

**Trade-offs**:
- **Cannot revoke**: JWTs valid until expiration (mitigated with short lifetimes + refresh tokens)
- **Size**: JWTs larger than opaque tokens (acceptable for HTTP headers)

### 3. In-Memory Storage

**Decision**: Use Python dictionaries for storing clients, codes, and tokens

**Rationale**:
- **Mock server simplicity**: No database dependencies
- **Fast**: Zero-latency lookups
- **Acceptable data loss**: Mock server can restart without state

**Trade-offs**:
- **Not production-ready**: Real implementations need persistent storage
- **No clustering**: Can't run multiple server instances

### 4. Auto-Approval Consent

**Decision**: Automatically approve all authorization requests

**Rationale**:
- **Testing convenience**: No manual intervention during development
- **Focus on protocol**: Demonstrates OAuth mechanics without UI complexity

**Trade-offs**:
- **Real servers must show consent UI**: Users need to review and approve permissions
- **Security consideration**: Production must never auto-approve

---

## Security Model

### Threat Mitigation

| Threat | Mitigation |
|--------|-----------|
| **Authorization code interception** | PKCE ensures only client with code_verifier can exchange code |
| **Token theft** | Short-lived access tokens (60 min), HTTPS-only in production |
| **Token replay** | Each auth code is single-use, marked as used after exchange |
| **Open redirect** | Server validates redirect_uri matches registered URIs exactly |
| **CSRF attacks** | State parameter validation (client-generated random value) |
| **Privilege escalation** | Scope validation, audience binding to specific MCP server |
| **Confused deputy** | Resource parameter ensures tokens only valid for specific server |

### Critical Security Properties

1. **Audience Binding**: Tokens must include `aud` claim with MCP server URI
2. **No Token Passthrough**: MCP server must never forward tokens to other services
3. **HTTPS in Production**: All OAuth endpoints must use TLS
4. **Localhost Exception**: Redirect URIs can be `http://localhost` for development
5. **Refresh Token Rotation**: Public clients should rotate refresh tokens (OAuth 2.1)

---

## When to Use This Approach

### ✅ Appropriate Use Cases

**1. Multi-User MCP Servers**
- SaaS platforms where each user has their own data
- Enterprise tools with user-specific permissions
- Systems requiring audit trails of AI actions

**2. Third-Party MCP Clients**
- AI applications connecting to various enterprise MCP servers
- Developer tools that integrate with multiple services
- Platforms aggregating data from different MCP sources

**3. Dynamic Integration Scenarios**
- Users connecting AI to new services without IT intervention
- Marketplace of MCP servers requiring standardized auth
- Rapid prototyping where manual registration is friction

**4. Security-Sensitive Environments**
- Healthcare, financial, or legal data requiring user consent
- Compliance requirements (GDPR, HIPAA) for access logging
- Zero-trust architectures requiring explicit authorization

### ❌ Not Recommended For

**1. Single-User Local Tools**
- Personal desktop applications with no sharing
- Development tools accessing local file systems
- STDIO-based MCP servers (use environment credentials instead)

**2. Trusted First-Party Integrations**
- Same organization owns both client and server
- Can use service accounts or API keys securely
- No user delegation needed

**3. High-Frequency, Low-Value Operations**
- Public data that doesn't require authorization
- Read-only access to non-sensitive information
- Scenarios where auth overhead outweighs security benefit

**4. Resource-Constrained Environments**
- Embedded systems without HTTP support
- Batch processing without user interaction
- Systems where OAuth flow is impossible (no browser, etc.)

---

## Alternative Approaches

### Comparison with Other Auth Methods

| Method | Best For | Limitations |
|--------|----------|-------------|
| **API Keys** | Server-to-server, single identity | No user delegation, shared secrets |
| **Basic Auth** | Simple authentication, internal tools | Credentials in every request, no scoping |
| **mTLS** | Machine identity, zero-trust networks | Complex PKI, no user context |
| **STDIO + Env Vars** | Local MCP servers, single-user CLIs | Not suitable for remote servers |
| **OAuth 2.0 (manual reg)** | Fixed set of integrations | Requires pre-registration |
| **OAuth 2.0 + DCR** | Dynamic integrations, multi-user | More complex, requires auth server |

---

## Future Considerations

### Potential Enhancements

1. **Token Revocation (RFC 7009)**
   - Allow users to revoke AI access immediately
   - Implement revocation endpoint and token introspection

2. **Rich Authorization Requests (RFC 9396)**
   - Fine-grained permissions ("read contacts" vs "write contacts")
   - Resource-specific scopes

3. **Federation and SSO**
   - Use enterprise identity provider (Google Workspace, Azure AD, Okta)
   - SAML or OpenID Connect integration

4. **Token Exchange (RFC 8693)**
   - MCP server acting as client to upstream APIs
   - Proper token audience binding and scope downgrading

5. **Device Flow (RFC 8628)**
   - Better UX for CLI tools and headless systems
   - User authorizes on phone/computer while device polls

---

## Implementation Checklist

When building a production MCP server with OAuth + DCR:

- [ ] **Use persistent storage** (PostgreSQL, Redis) for clients, codes, tokens
- [ ] **Implement consent UI** showing what permissions AI requests
- [ ] **Add token revocation** so users can terminate access
- [ ] **Use HTTPS everywhere** (except localhost for development)
- [ ] **Add rate limiting** on registration and token endpoints
- [ ] **Log all authorization events** for audit and security monitoring
- [ ] **Validate redirect URIs strictly** (exact match, no wildcards)
- [ ] **Implement refresh token rotation** for public clients
- [ ] **Add audience claims to JWTs** and validate them
- [ ] **Support CORS** if web-based clients will connect
- [ ] **Document scopes clearly** so users understand permissions
- [ ] **Test token expiration** and refresh flow thoroughly
- [ ] **Consider multi-tenancy** if hosting multiple resource servers

---

## Conclusion

OAuth 2.0 + Dynamic Client Registration transforms MCP from a **developer-focused protocol** into an **enterprise-ready platform**. It enables:

- **User-centric authorization**: AI acts on behalf of users with their explicit consent
- **Zero-touch onboarding**: Automatic client registration eliminates setup friction
- **Enterprise security**: Token-based auth with scoping, expiration, and revocation
- **Audit and compliance**: Clear trails of who accessed what, when

This approach is **essential for multi-user SaaS MCP servers** and **third-party AI integrations** but may be **overkill for single-user local tools**. Choose based on your security requirements, user model, and operational constraints.

The reference implementation in this repository demonstrates **all the core concepts** and can serve as a **template for production deployments** with appropriate hardening and infrastructure changes.
