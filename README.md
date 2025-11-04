# MCP OAuth DCR Client

> **AI agent authorization client**: Dynamic Client Registration + OAuth 2.0 for the Model Context Protocol

This repository provides a **production-ready client implementation** for connecting to MCP servers using **Dynamic Client Registration (DCR)** and **OAuth 2.0 Authorization**. This enables AI applications to securely access user-authorized enterprise tools and data without manual client registration or pre-shared credentials.

[![Tests](https://github.com/kgang/superdynamic/actions/workflows/test.yml/badge.svg)](https://github.com/kgang/superdynamic/actions/workflows/test.yml)
[![MCP Spec](https://img.shields.io/badge/MCP%20Spec-2025--06--18-blue)](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization)
[![RFC 7591](https://img.shields.io/badge/RFC%207591-DCR-green)](https://datatracker.ietf.org/doc/html/rfc7591)
[![RFC 7636](https://img.shields.io/badge/RFC%207636-PKCE-green)](https://datatracker.ietf.org/doc/html/rfc7636)

---

## 🎯 Project Purpose

**This project provides a production-ready CLIENT for connecting AI applications to MCP servers using Dynamic Client Registration.**

- **Main Deliverable:** `client.py` - A Python client that implements DCR + OAuth 2.0 for MCP servers
- **Supporting Infrastructure:** `server/` - A reference MCP server for testing (development/testing only)

**Use the client** to connect your AI application to any MCP server supporting DCR (enterprise tools, custom data sources, etc.)

**Use the server** to test your client implementation without needing access to production MCP servers.

---

## What is This?

This is a **client implementation** for connecting AI applications to MCP servers that support Dynamic Client Registration and OAuth 2.0 authorization, based on the [MCP Authorization Specification](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization).

### The Client (`client.py`)

The main deliverable is a **Python-based MCP OAuth DCR Client** that can:

- ✅ **Automatically register** with any MCP server supporting DCR (RFC 7591)
- ✅ **Handle OAuth 2.0 authorization** with PKCE (RFC 7636) for secure public clients
- ✅ **Manage multi-server connections** with persistent credential storage
- ✅ **Execute authenticated MCP tool calls** with automatic token handling
- ✅ **Refresh tokens** automatically when they expire
- ✅ **Provide clear error messages** for debugging authorization failures

### The Reference Server (For Testing Only)

To enable testing without requiring access to a real DCR-enabled MCP server, this repository also includes:

- 📦 **Reference MCP server** with OAuth 2.0 + DCR support
- 📦 **Docker-based deployment** for quick local testing
- 📦 **Example MCP tools** (weather, files, user profile)

**Note:** The server implementation is provided solely for testing and educational purposes. In production, you would connect the client to real enterprise MCP servers (Google Workspace, Salesforce, etc.) that support DCR.

### Why Does This Matter?

The MCP Authorization Specification (released ~2 months ago) unlocks a powerful new paradigm for AI applications:

- **Dynamic enterprise access**: Connect to any DCR-enabled MCP server without pre-configuration
- **User-centric AI**: AI agents acting on behalf of users with explicit OAuth consent
- **Zero-touch onboarding**: No manual client registration, API key management, or credential sharing
- **Enterprise-grade security**: Token-based auth with scoping, expiration, and audit trails

This client enables your AI application to seamlessly integrate with the emerging ecosystem of MCP servers across enterprise tools (Google Workspace, Salesforce, etc.) and custom data sources.

**The Challenge:** While the MCP Authorization spec is only ~2 months old, there are minimal production examples showing how to implement the full DCR + OAuth flow from the client side. This implementation provides a clear, tested reference for building clients that can leverage this new capability.

---

## Requirements

- **Python 3.10+** (tested on 3.10, 3.11, 3.12)
- **Docker** (optional, for containerized deployment)

## Quick Start

### ⚡ Fastest Way

```bash
# One-command demo (starts test server + runs client)
./quickstart.sh
```

This script will:
1. Install dependencies
2. Start the **reference test server**
3. Let you choose between automated test or interactive demo

### Manual Setup

#### 1. Start the Test Server (for development/testing)

```bash
cd server
docker-compose up --build
```

Test server available at: `http://localhost:8000`

- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

**Note:** In production, you would skip this step and connect directly to a real MCP server URL that supports DCR.

#### 2. Use the Client

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

This client implements the full MCP authorization flow from the client perspective:

```
┌──────────────┐                           ┌───────────────────────┐
│              │  1. Discover metadata     │                       │
│              │ ────────────────────────► │   MCP Server          │
│  MCP Client  │                           │   (Resource Server)   │
│  (client.py) │  2. Register via DCR      │                       │
│              │ ────────────────────────► │   + OAuth 2.0 Server  │
│              │  ← Get client_id/secret   │                       │
│              │                           │   - Issues tokens     │
│              │  3. User authorization    │   - Validates PKCE    │
│              │ ◄───────────────────────► │   - Executes tools    │
│              │  ← Get auth code + token  │                       │
│              │                           │                       │
│              │  4. Call MCP tools        │                       │
│              │ ────────────────────────► │                       │
│              │    (Bearer token auth)    │                       │
└──────────────┘                           └───────────────────────┘
```

**Client Features:**
- Metadata discovery (RFC 8414, RFC 9728)
- Dynamic Client Registration (RFC 7591)
- OAuth 2.0 Authorization Code Flow with PKCE (RFC 7636)
- Token management (refresh, expiration checking)
- MCP JSON-RPC 2.0 protocol implementation

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed design rationale and use cases.

---

## Key Features

### 1. Client Implementation (`client.py`)

The production-ready client that your AI application uses:

**Dynamic Client Registration (RFC 7591):**
```python
# Client automatically registers with any MCP server
python client.py --server-url https://mcp.example.com --register

# Response stored in .mcp_clients.json:
# - client_id
# - client_secret
# - token_endpoint
# - authorization_endpoint
```

**OAuth 2.0 with PKCE (RFC 7636):**
- Automatic S256 code challenge generation
- Browser-based authorization flow
- Secure code verifier validation
- Automatic token refresh handling
- Multi-server credential management

**MCP Protocol Implementation:**
- JSON-RPC 2.0 tool invocation
- Bearer token authentication
- Clear error handling and reporting
- Persistent token storage

### 2. Reference Test Server (Development Only)

To facilitate testing without enterprise MCP servers, we provide a mock server with:

- **OAuth 2.0 Server**: Token issuance, PKCE validation, DCR endpoint
- **MCP Server**: Three example tools (weather, files, user_profile)
- **Docker deployment**: Quick local setup for development

**Note:** This server is for testing only. In production, you connect the client to real MCP servers.

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
├── client.py                 # 🎯 MCP OAuth DCR Client (MAIN DELIVERABLE)
├── requirements.txt          # Client dependencies
├── .mcp_clients.json        # Persistent client storage (created on first run)
│
├── ARCHITECTURE.md           # Design rationale and use cases
├── FLOW_DIAGRAM.md           # Visual authorization flow walkthrough
├── mcp_auth_spec_summary.md  # MCP Authorization Spec summary
├── requirements.md           # Technical requirements
├── claude.md                 # Development session notes
│
├── security/                 # Security audits and assessments
│   ├── README.md                   # Security overview
│   ├── components/                 # Component-specific audits
│   │   ├── CLIENT_SECURITY_AUDIT.md  # Client security review
│   │   └── SERVER_SECURITY_AUDIT.md  # Server security review
│   └── complete-audits/            # System-wide assessments
│       ├── IMPLEMENTATION_SUMMARY.md
│       ├── LLM_CODE_ASSESSMENT_FRAMEWORK.md
│       ├── VERIFIED_CRITICAL_FINDINGS.md
│       └── ASSESSMENT_SUMMARY.md
│
├── tests/                    # Test suite
│   ├── conftest.py          # Pytest fixtures
│   ├── test_client.py       # Client integration tests
│   ├── test_security_vulnerabilities.py # Security tests
│   ├── README.md            # Test documentation
│   └── server/
│       └── test_flow.py     # Server OAuth flow tests
│
└── server/                   # 📦 REFERENCE TEST SERVER (for development/testing)
    ├── app/
    │   ├── main.py          # FastAPI application
    │   ├── oauth/           # OAuth 2.0 + DCR implementation
    │   │   ├── dcr.py       # Dynamic Client Registration
    │   │   ├── authorize.py # Authorization endpoint
    │   │   ├── token.py     # Token endpoint
    │   │   ├── pkce.py      # PKCE utilities
    │   │   └── metadata.py  # Discovery endpoints
    │   └── mcp/             # MCP protocol implementation
    │       ├── protocol.py  # JSON-RPC handler
    │       └── tools.py     # Example tools
    ├── Dockerfile
    ├── docker-compose.yml
    └── README.md            # Server documentation
```

**Key Components:**
- **`client.py`**: The production client you integrate into your AI application
- **`server/`**: A reference server for testing the client without enterprise MCP servers
- **`security/`**: Comprehensive security audits of both client and server
- **`tests/`**: Full test suite including end-to-end OAuth flows

---

## When to Use This Client

### ✅ Use This Client When

Your AI application needs to:

- **Connect to multiple MCP servers dynamically** (Google Workspace, Salesforce, custom enterprise tools)
- **Act on behalf of users** with OAuth consent and user-scoped permissions
- **Avoid manual credential management** (no API keys, pre-registration, or credential sharing)
- **Meet enterprise security requirements** (token-based auth, audit trails, expiration)
- **Support multi-tenant SaaS** where each user connects to their own data sources

### ❌ Don't Use This Client For

- **Single-user local tools** (use API keys or environment variables instead)
- **Public data access** (no authorization needed)
- **STDIO-based MCP servers** (use environment credentials instead)
- **First-party integrations** where you control both the client and server (simpler auth is fine)

### When to Use the MCP DCR/OAuth Standard (Server Side)

MCP servers should implement DCR + OAuth when:

- ✅ Supporting **multi-user SaaS** (each user has their own data)
- ✅ Enabling **third-party AI integrations** to your platform
- ✅ Requiring **security/compliance** (audit trails, user consent, token expiration)

MCP servers should **NOT** implement DCR + OAuth for:

- ❌ **Single-user local tools**
- ❌ **Trusted first-party integrations**
- ❌ **Public data** with no access control needs

See [ARCHITECTURE.md § When to Use This Approach](ARCHITECTURE.md#when-to-use-this-approach) for detailed guidance.

---

## Security Considerations

### Client Security (`client.py`)

The client implements OAuth 2.0 security best practices:

**✅ Implemented Security Controls:**
- ✅ **PKCE (S256)** - Prevents authorization code interception attacks
- ✅ **Secure credential storage** - Client credentials and tokens stored locally in `.mcp_clients.json`
- ✅ **Automatic token refresh** - Handles token expiration gracefully
- ✅ **JWT signature verification** - Validates tokens from the server
- ✅ **Bearer token authentication** - Proper Authorization header usage
- ✅ **Redirect URI validation** - Ensures callbacks go to expected locations

**⚠️ Production Considerations:**
- Ensure `.mcp_clients.json` has appropriate file permissions (not world-readable)
- Use HTTPS for all MCP server connections in production
- Consider encrypting stored credentials at rest for additional security
- Implement proper token revocation when disconnecting from servers

**See:** [security/components/CLIENT_SECURITY_AUDIT.md](security/components/CLIENT_SECURITY_AUDIT.md)

### Test Server Security (`server/`)

The reference test server is **for development/testing only** and includes:

**✅ Development Features:**
- ✅ Auto-approval of OAuth requests (no consent UI)
- ✅ In-memory storage (data lost on restart)
- ✅ HTTP support for localhost testing

**🔴 NOT for Production:**
1. Lacks persistent storage
2. No user consent UI
3. Simplified token validation
4. Missing JWT audience claims
5. No refresh token rotation

**See:** [security/components/SERVER_SECURITY_AUDIT.md](security/components/SERVER_SECURITY_AUDIT.md)

---

**For Production:** Use real MCP servers (Google Workspace, Salesforce, etc.) with production-grade OAuth implementations. The client is production-ready; the server is not.

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

This is a production-ready client implementation with a reference test server. Contributions welcome for:

- **Client enhancements**: Additional OAuth flows, error handling improvements, security features
- **Documentation improvements**: Usage examples, integration guides, troubleshooting tips
- **Test coverage**: Additional integration tests, security tests, edge cases
- **Server improvements**: Additional example MCP tools for testing, better OAuth flows
- **Client examples**: Integration examples with popular AI frameworks

---

## License

MIT License - See LICENSE file for details

---

## Acknowledgments

This client implementation was built using **Claude Code** as part of an exploration of LLM-driven development for implementing complex security specifications.

Special thanks to:
- The **MCP specification authors** at Anthropic for designing a clean authorization model that balances security and developer experience
- The OAuth working group for RFC 7591 (DCR) and RFC 7636 (PKCE)

**Note:** This project demonstrates both a production-ready **client** and a reference **server** for testing. The client (`client.py`) is designed for production use; the server (`server/`) is for development and testing only.

---

## Further Reading

- [Model Context Protocol](https://modelcontextprotocol.io/)
- [MCP Authorization Specification](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization)
- [OAuth 2.1 Security Best Practices](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-v2-1)
- [PKCE Explanation](https://auth0.com/docs/get-started/authentication-and-authorization-flow/authorization-code-flow-with-proof-key-for-code-exchange-pkce)

---

**Ready to integrate?**
1. Review [security/components/CLIENT_SECURITY_AUDIT.md](security/components/CLIENT_SECURITY_AUDIT.md) for production best practices
2. Test with the reference server: `./quickstart.sh`
3. Connect to real MCP servers by updating the `--server-url` parameter

**Questions?** See documentation or open an issue.
