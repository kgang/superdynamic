# MCP OAuth DCR Reference Implementation

> **AI agent authorization infrastructure**: Dynamic Client Registration + OAuth 2.0 for the Model Context Protocol

This repository demonstrates how to implement **OAuth 2.0 Authorization** with **Dynamic Client Registration (DCR)** for the **Model Context Protocol (MCP)**, enabling AI applications to securely access user-authorized enterprise tools and data.

[![Tests](https://github.com/kgang/superdynamic/actions/workflows/test.yml/badge.svg)](https://github.com/kgang/superdynamic/actions/workflows/test.yml)
[![MCP Spec](https://img.shields.io/badge/MCP%20Spec-2025--06--18-blue)](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization)
[![RFC 7591](https://img.shields.io/badge/RFC%207591-DCR-green)](https://datatracker.ietf.org/doc/html/rfc7591)
[![RFC 7636](https://img.shields.io/badge/RFC%207636-PKCE-green)](https://datatracker.ietf.org/doc/html/rfc7636)

---

## What is This?

This is a **reference implementation** and **educational resource** for understanding and implementing the [MCP Authorization Specification](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization). It includes:

- ✅ **Complete OAuth 2.0 Authorization Server** with Dynamic Client Registration (RFC 7591)
- ✅ **MCP Server** with authenticated tool invocation
- ✅ **PKCE Support** (RFC 7636) for secure public clients
- ✅ **Docker-based deployment** for easy testing
- ✅ **Comprehensive documentation** of architecture and security model
- ✅ **Working examples** demonstrating the full authorization flow

### Why Does This Matter?

The MCP Authorization Specification (released ~2 months ago) enables:
- **User-centric AI**: AI agents acting on behalf of users with explicit consent
- **Zero-touch onboarding**: Automatic client registration without manual setup
- **Enterprise security**: Token-based auth with scoping, expiration, and audit trails
- **Dynamic integrations**: Connect to arbitrary MCP servers without pre-registration

This is **essential for multi-user SaaS platforms** and **third-party AI integrations** but relatively new with minimal production examples.

---

## Requirements

- **Python 3.10+** (tested on 3.10, 3.11, 3.12)
- **Docker** (optional, for containerized deployment)

## Quick Start

### ⚡ Fastest Way

```bash
# One-command demo (starts server + runs client)
./quickstart.sh
```

This script will:
1. Install dependencies
2. Start the MCP server
3. Let you choose between automated test or interactive demo

### Manual Setup

#### Run the Server

```bash
cd server
docker-compose up --build
```

Server available at: `http://localhost:8000`

- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### Use the Client

The client provides a complete implementation of DCR + OAuth flow with multi-client lifecycle management:

```bash
# Install client dependencies
pip install -r requirements.txt

# Run the full demo (interactive - opens browser for authorization)
python client.py --server-url http://localhost:8000 --demo

# Or use individual commands:

# Register a new OAuth client
python client.py --server-url http://localhost:8000 --register

# Authorize (opens browser)
python client.py --server-url http://localhost:8000 --authorize

# List available tools
python client.py --server-url http://localhost:8000 --list-tools

# Call a tool
python client.py --server-url http://localhost:8000 --call-tool get_weather \
  --args '{"location": "San Francisco", "units": "fahrenheit"}'

# List all registered clients
python client.py --list-clients

# Refresh access token
python client.py --server-url http://localhost:8000 --refresh
```

**Client Features:**
- ✅ Dynamic Client Registration (RFC 7591)
- ✅ OAuth 2.0 Authorization Code Flow with PKCE
- ✅ Automatic browser-based authorization
- ✅ Token refresh handling
- ✅ Multi-client lifecycle management (manage OAuth clients for multiple MCP servers)
- ✅ Persistent storage of client credentials and tokens
- ✅ Automatic token expiration checking

### Test the Full Flow

```bash
# Test server endpoints programmatically
pytest tests/server/test_flow.py

# Test client with mock authorization (no browser required)
pytest tests/test_client.py
```

This demonstrates:
1. Dynamic Client Registration
2. PKCE parameter generation
3. OAuth authorization code flow
4. Token exchange
5. Authenticated MCP tool invocation
6. Token refresh
7. Multi-client management

---

## Architecture Overview

```
┌──────────────┐                           ┌───────────────────────┐
│              │  1. Discover metadata     │                       │
│              │ ────────────────────────► │   MCP Server          │
│   AI Agent   │                           │   (Resource Server)   │
│   (Client)   │  2. Register via DCR      │                       │
│              │ ────────────────────────► │   + OAuth 2.0 Server  │
│              │                           │                       │
│              │  3. User authorization    │   - Issues tokens     │
│              │ ◄───────────────────────► │   - Validates PKCE    │
│              │                           │   - Executes tools    │
│              │  4. Call MCP tools        │                       │
│              │ ────────────────────────► │                       │
│              │    (Bearer token auth)    │                       │
└──────────────┘                           └───────────────────────┘
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed design rationale and use cases.

---

## Key Features

### 1. Dynamic Client Registration (RFC 7591)

Clients self-register without manual intervention:

```bash
POST /oauth/register
{
  "redirect_uris": ["http://localhost:3000/callback"],
  "client_name": "My AI Assistant"
}

# Response: client_id, client_secret
```

### 2. OAuth 2.0 with PKCE (RFC 7636)

Secure authorization code flow for public clients:
- S256 code challenge generation
- Authorization endpoint with auto-approval (dev mode)
- Token endpoint with code verifier validation
- Refresh token support

### 3. MCP Protocol Implementation

JSON-RPC 2.0 based tool invocation:
- `POST /mcp/initialize` - Server handshake (no auth)
- `POST /mcp/tools/list` - List available tools (requires auth)
- `POST /mcp/tools/call` - Execute tool (requires auth)

### 4. Three Example Tools

1. **get_weather** - Mock weather data
2. **list_files** - Mock file system
3. **get_user_profile** - User info from token claims

---

## Documentation

| Document | Purpose |
|----------|---------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | Design rationale, use cases, and "when to use" guidance |
| [security/](security/) | Comprehensive security audits for server and client |
| [FLOW_DIAGRAM.md](FLOW_DIAGRAM.md) | Visual walkthrough of the complete authorization flow |
| [server/README.md](server/README.md) | Detailed API documentation and usage examples |
| [mcp_auth_spec_summary.md](mcp_auth_spec_summary.md) | Summary of the MCP Authorization Specification |
| [claude.md](claude.md) | Development session notes and decision log |

---

## Standards Implemented

- **[RFC 7591](https://datatracker.ietf.org/doc/html/rfc7591)** - OAuth 2.0 Dynamic Client Registration Protocol
- **[RFC 7636](https://datatracker.ietf.org/doc/html/rfc7636)** - Proof Key for Code Exchange (PKCE)
- **[RFC 6749](https://datatracker.ietf.org/doc/html/rfc6749)** - OAuth 2.0 Authorization Framework
- **[RFC 8414](https://datatracker.ietf.org/doc/html/rfc8414)** - OAuth 2.0 Authorization Server Metadata
- **[RFC 9728](https://datatracker.ietf.org/doc/html/rfc9728)** - OAuth 2.0 Protected Resource Metadata
- **[MCP Authorization Spec (2025-06-18)](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization)** - Model Context Protocol Authorization

---

## Project Structure

```
├── ARCHITECTURE.md           # Design synthesis and use cases
├── FLOW_DIAGRAM.md           # Visual authorization flow
├── IMPLEMENTATION_SUMMARY.md # Comprehensive implementation and security fixes
├── mcp_auth_spec_summary.md  # MCP spec summary
├── claude.md                 # Development session notes
├── requirements.md           # Technical requirements
├── requirements.txt          # Client dependencies
├── client.py                 # MCP OAuth DCR Client (main deliverable)
├── test_client.py            # Client integration test
├── security/                 # Security audits and assessments
│   ├── README.md                   # Security overview
│   ├── components/                 # Component-specific audits
│   │   ├── SERVER_SECURITY_AUDIT.md
│   │   └── CLIENT_SECURITY_AUDIT.md
│   └── complete-audits/            # System-wide assessments
│       ├── LLM_CODE_ASSESSMENT_FRAMEWORK.md
│       ├── VERIFIED_CRITICAL_FINDINGS.md
│       └── ASSESSMENT_SUMMARY.md
├── tests/                    # Test suite
│   ├── conftest.py          # Pytest fixtures
│   ├── test_client.py       # Client integration tests
│   ├── test_security_vulnerabilities.py # Security tests
│   ├── README.md            # Test documentation
│   └── server/
│       └── test_flow.py     # Server OAuth flow tests
└── server/                   # Mock MCP server implementation
    ├── app/
    │   ├── main.py          # FastAPI application
    │   ├── oauth/           # OAuth 2.0 implementation
    │   │   ├── dcr.py       # Dynamic Client Registration
    │   │   ├── authorize.py # Authorization endpoint
    │   │   ├── token.py     # Token endpoint
    │   │   ├── pkce.py      # PKCE utilities
    │   │   └── metadata.py  # Discovery endpoints
    │   └── mcp/             # MCP protocol
    │       ├── protocol.py  # JSON-RPC handler
    │       └── tools.py     # Example tools
    ├── Dockerfile
    ├── docker-compose.yml
    └── README.md            # Server-specific documentation
```

---

## When to Use This Approach

### ✅ Recommended For

- **Multi-user SaaS MCP servers** (each user has their own data)
- **Third-party AI integrations** (connecting to various enterprise systems)
- **Dynamic onboarding scenarios** (no manual registration)
- **Security/compliance requirements** (audit trails, user consent, token expiration)

### ❌ Not Recommended For

- **Single-user local tools** (use API keys or environment variables)
- **Trusted first-party integrations** (same organization owns both sides)
- **Public data access** (no authorization needed)
- **STDIO-based MCP servers** (use environment credentials instead)

See [ARCHITECTURE.md § When to Use This Approach](ARCHITECTURE.md#when-to-use-this-approach) for detailed guidance.

---

## Security Considerations

### ✅ Implemented Security Controls

- ✅ PKCE (S256) prevents authorization code interception
- ✅ Single-use authorization codes
- ✅ Short-lived access tokens (60 min default)
- ✅ Refresh token support
- ✅ Redirect URI validation
- ✅ JWT signature verification
- ✅ Bearer token authentication
- ✅ WWW-Authenticate headers on 401 responses

### ⚠️ Development-Only Features

- **Auto-approval**: Authorization requests automatically approved (no consent UI)
- **In-memory storage**: Data lost on restart
- **HTTP allowed**: Production requires HTTPS

### 🔴 Production Enhancements Needed

1. **Add JWT audience claims** (`aud`) and validate them
2. **Implement user consent UI** for authorization requests
3. **Use HTTPS** for all endpoints
4. **Persistent storage** (PostgreSQL, Redis, etc.)
5. **Refresh token rotation** (OAuth 2.1 recommendation)

See [security/](security/) for comprehensive security audits of both server and client components.

---

## Development

### Local Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r server/requirements.txt

# Run server
uvicorn server.app.main:app --reload

# Or use the helper script
cd server && ./run.sh
```

### Environment Configuration

See `server/docker-compose.yml` for available environment variables:

- `JWT_SECRET_KEY` - Secret for signing JWTs
- `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` - Token lifetime (default: 60)
- `OAUTH_AUTHORIZATION_CODE_EXPIRE_MINUTES` - Auth code lifetime (default: 10)
- `SERVER_URL` - Server base URL
- `DEBUG` - Debug mode (default: true)

---

## Testing

### End-to-End Flow Test

```bash
# Start server in one terminal
cd server
docker-compose up

# Run test in another terminal
pytest tests/server/test_flow.py
```

**Test Coverage**:
1. ✅ Dynamic Client Registration
2. ✅ PKCE code challenge/verifier generation
3. ✅ Authorization request
4. ✅ Token exchange with PKCE validation
5. ✅ MCP tool listing
6. ✅ Authenticated tool execution
7. ✅ Token refresh

### Manual Testing with cURL

See [server/README.md § Example Flow](server/README.md#example-flow) for detailed cURL examples.

---

## Troubleshooting

### Server Issues

**Server won't start:**
```bash
# Check if port 8000 is already in use
lsof -i :8000
# Kill the process if needed
kill -9 <PID>
```

**Import errors:**
```bash
# Ensure all dependencies are installed
pip install -r server/requirements.txt
pip install -r requirements.txt
```

**JWT/Cryptography errors:**
```bash
# Reinstall cryptography dependencies
pip install --force-reinstall cffi cryptography
```

### Client Issues

**Browser doesn't open for OAuth:**
- Manually copy the authorization URL from the terminal
- Paste it into your browser
- The redirect should still work

**"Connection refused" errors:**
- Ensure the server is running: `curl http://localhost:8000/health`
- Check that you're using the correct server URL
- Verify no firewall is blocking localhost:8000

**Client storage issues:**
```bash
# Reset client storage
rm .mcp_clients.json
# Re-register client
python client.py --server-url http://localhost:8000 --register
```

**Token expired errors:**
```bash
# Refresh the token
python client.py --server-url http://localhost:8000 --refresh
# Or re-authorize
python client.py --server-url http://localhost:8000 --authorize
```

### Common Environment Issues

**Python version too old:**
```bash
# Check version
python3 --version
# Needs Python 3.10 or higher
```

**Docker Compose issues:**
```bash
# Use docker compose (v2) instead of docker-compose (v1)
docker compose up --build

# Or install docker-compose v1
sudo apt install docker-compose
```

### Getting Help

1. Check the [server logs](server/server.log) or terminal output
2. Review [ARCHITECTURE.md](ARCHITECTURE.md) for design details
3. See [security/](security/) for security audits and recommendations
4. Open an issue with:
   - Python version (`python3 --version`)
   - Error message and full traceback
   - Steps to reproduce

---

## Contributing

This is a reference implementation for educational purposes. Contributions welcome for:

- Additional MCP tool examples
- Security enhancements
- Documentation improvements
- Client implementation examples
- Integration tests

---

## License

MIT License - See LICENSE file for details

---

## Acknowledgments

Built using **Claude Code** as part of an exploration of LLM-driven development for implementing complex security specifications.

Special thanks to the **MCP specification authors** at Anthropic for designing a clean authorization model that balances security and developer experience.

---

## Further Reading

- [Model Context Protocol](https://modelcontextprotocol.io/)
- [MCP Authorization Specification](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization)
- [OAuth 2.1 Security Best Practices](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-v2-1)
- [PKCE Explanation](https://auth0.com/docs/get-started/authentication-and-authorization-flow/authorization-code-flow-with-proof-key-for-code-exchange-pkce)

---

**Questions?** See documentation or open an issue.

**Ready to deploy?** Review [security/](security/) for production readiness checklists and security recommendations.
