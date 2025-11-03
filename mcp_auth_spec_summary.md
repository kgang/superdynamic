# MCP Authorization Specification Summary

## Overview
The Model Context Protocol (MCP) provides **optional** authorization capabilities at the transport level, enabling MCP clients to make requests to restricted MCP servers on behalf of resource owners. This is based on OAuth 2.1 and related standards.

## Transport-Specific Requirements
- **HTTP-based transports**: SHOULD follow this specification
- **STDIO transports**: SHOULD NOT use this spec (retrieve credentials from environment instead)
- **Alternative transports**: MUST follow established security best practices for their protocol

## Core Standards Compliance
The authorization mechanism implements selected subsets of:
- OAuth 2.1 (draft-ietf-oauth-v2-1-13)
- OAuth 2.0 Authorization Server Metadata (RFC8414)
- OAuth 2.0 Dynamic Client Registration Protocol (RFC7591)
- OAuth 2.0 Protected Resource Metadata (RFC9728)

## Key Roles
1. **MCP Server**: Acts as OAuth 2.1 resource server, accepts protected resource requests using access tokens
2. **MCP Client**: Acts as OAuth 2.1 client, makes protected requests on behalf of resource owner
3. **Authorization Server**: Issues access tokens for use at the MCP server (may be hosted with resource server or separately)

## Authorization Flow

### 1. Authorization Server Discovery
**MCP servers MUST:**
- Implement OAuth 2.0 Protected Resource Metadata (RFC9728)
- Include `authorization_servers` field with at least one authorization server
- Use `WWW-Authenticate` header when returning 401 Unauthorized to indicate resource server metadata URL

**MCP clients MUST:**
- Use OAuth 2.0 Protected Resource Metadata for discovery
- Parse `WWW-Authenticate` headers and respond to 401 responses
- Follow OAuth 2.0 Authorization Server Metadata (RFC8414) to obtain authorization server information

### 2. Dynamic Client Registration
**SHOULD be supported** by both MCP clients and authorization servers (RFC7591) to:
- Allow automatic registration without user interaction
- Enable seamless connection to new MCP servers
- Avoid manual registration friction

Fallback options if not supported:
- Hardcode client ID/credentials for specific authorization servers
- Present UI for users to manually enter registration details

### 3. Resource Parameter Implementation
**MCP clients MUST** implement Resource Indicators (RFC 8707):
- Include `resource` parameter in authorization AND token requests
- Use canonical URI of the MCP server
- Provide the most specific URI possible

**Canonical URI format:**
- Valid: `https://mcp.example.com`, `https://mcp.example.com:8443`, `https://mcp.example.com/server/mcp`
- Invalid: `mcp.example.com` (missing scheme), `https://mcp.example.com#fragment` (contains fragment)
- Prefer without trailing slash unless semantically significant

### 4. Access Token Usage

**Token Requirements:**
- MUST use Authorization header: `Authorization: Bearer <token>`
- MUST NOT include tokens in URI query string

**Token Handling:**
- MCP servers MUST validate tokens per OAuth 2.1 Section 5.2
- MUST validate tokens were issued specifically for them (audience validation)
- Invalid/expired tokens MUST receive HTTP 401 response
- MCP clients MUST NOT send tokens from other authorization servers
- MCP servers MUST NOT accept or transit other tokens

## Error Handling
Required HTTP status codes:
- **401 Unauthorized**: Authorization required or token invalid
- **403 Forbidden**: Invalid scopes or insufficient permissions
- **400 Bad Request**: Malformed authorization request

## Critical Security Considerations

### 1. Token Audience Binding and Validation
- Clients MUST include `resource` parameter in all requests
- Servers MUST validate tokens were specifically issued for their use
- Prevents token reuse across different services

### 2. Token Theft Prevention
- Implement secure token storage
- Use short-lived access tokens
- Rotate refresh tokens for public clients (OAuth 2.1 Section 4.3.1)

### 3. Communication Security
- All authorization server endpoints MUST use HTTPS
- Redirect URIs MUST be either `localhost` or HTTPS

### 4. Authorization Code Protection
- MCP clients MUST implement PKCE (OAuth 2.1 Section 7.5.2)
- Prevents authorization code interception and injection attacks

### 5. Open Redirection Prevention
- Clients MUST have redirect URIs registered with authorization server
- Authorization servers MUST validate exact redirect URIs
- Clients SHOULD use and verify state parameters

### 6. Confused Deputy Problem
- MCP proxy servers using static client IDs MUST obtain user consent for each dynamically registered client
- Prevents exploitation when MCP servers act as intermediaries

### 7. Access Token Privilege Restriction
Two critical dimensions:
- **Audience validation failures**: Servers must verify tokens are intended for them
- **Token passthrough**: Servers MUST NOT forward unmodified tokens to downstream services
- If MCP server acts as OAuth client to upstream APIs, it must obtain separate tokens

## Complete Authorization Flow Steps
1. Client discovers MCP server's authorization server via Protected Resource Metadata
2. Client obtains authorization server metadata
3. Client optionally registers dynamically with authorization server
4. Client initiates authorization request with `resource` parameter and PKCE
5. User authorizes at authorization server
6. Client exchanges authorization code for tokens (with PKCE verifier)
7. Client includes access token in Authorization header for MCP requests
8. MCP server validates token audience and processes request

## Key Implementation Notes
- Authorization is OPTIONAL for MCP implementations
- When implemented, strict adherence to OAuth 2.1 security best practices is required
- Token passthrough is explicitly forbidden for security
- All implementations must follow the principle of least privilege
- Servers should only accept tokens specifically issued for them
