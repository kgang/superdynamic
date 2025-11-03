# MCP OAuth DCR Server

A mock Model Context Protocol (MCP) server implementing OAuth 2.0 Authorization Server with Dynamic Client Registration (DCR).

## Features

- ✅ **Dynamic Client Registration (RFC 7591)** - Clients can self-register without pre-configuration
- ✅ **OAuth 2.0 Authorization Code Flow with PKCE (RFC 7636)** - Secure authorization for public clients
- ✅ **OAuth 2.0 Authorization Server Metadata (RFC 8414)** - Server discovery
- ✅ **OAuth 2.0 Protected Resource Metadata (RFC 9728)** - MCP-specific resource metadata
- ✅ **Token Refresh** - Long-lived sessions with refresh tokens
- ✅ **MCP Protocol** - JSON-RPC 2.0 based tool invocation
- ✅ **Example Tools** - Weather, file listing, and user profile tools
- ✅ **Docker Support** - Easy deployment with Docker

## Quick Start

### Option 1: Docker (Recommended)

```bash
# Build and run with Docker Compose
cd server
docker-compose up --build

# Server will be available at http://localhost:8000
```

### Option 2: Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run server
python -m app.main

# Or use uvicorn directly
uvicorn app.main:app --reload
```

## API Endpoints

### OAuth Metadata

- `GET /.well-known/oauth-authorization-server` - Authorization server metadata
- `GET /.well-known/oauth-protected-resource` - Protected resource metadata

### OAuth Flow

1. **Register Client**: `POST /oauth/register`
2. **Authorize**: `GET /oauth/authorize`
3. **Get Token**: `POST /oauth/token`

### MCP Protocol

- `POST /mcp/initialize` - Initialize MCP session (no auth required)
- `POST /mcp/tools/list` - List available tools (requires auth)
- `POST /mcp/tools/call` - Execute a tool (requires auth)

### Documentation

- `GET /` - API overview
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation (ReDoc)
- `GET /health` - Health check endpoint

## Example Flow

See `tests/test_flow.py` for a complete end-to-end example. Here's a quick overview:

### 1. Register Client

```bash
curl -X POST http://localhost:8000/oauth/register \
  -H "Content-Type: application/json" \
  -d '{
    "redirect_uris": ["http://localhost:3000/callback"],
    "client_name": "My MCP Client"
  }'
```

Response:
```json
{
  "client_id": "client_abc123...",
  "client_secret": "secret_xyz789...",
  "redirect_uris": ["http://localhost:3000/callback"],
  ...
}
```

### 2. Generate PKCE Parameters

```python
import hashlib
import base64
import secrets

# Generate code verifier
code_verifier = base64.urlsafe_b64encode(
    secrets.token_bytes(32)
).decode('utf-8').rstrip('=')

# Generate code challenge
digest = hashlib.sha256(code_verifier.encode('utf-8')).digest()
code_challenge = base64.urlsafe_b64encode(digest).decode('utf-8').rstrip('=')
```

### 3. Authorization Request

```bash
# Visit this URL in browser (or use httpx/requests)
http://localhost:8000/oauth/authorize?response_type=code&client_id=CLIENT_ID&redirect_uri=http://localhost:3000/callback&code_challenge=CODE_CHALLENGE&code_challenge_method=S256&state=random123
```

You'll be redirected to:
```
http://localhost:3000/callback?code=AUTH_CODE&state=random123
```

### 4. Exchange Code for Token

```bash
curl -X POST http://localhost:8000/oauth/token \
  -d "grant_type=authorization_code" \
  -d "code=AUTH_CODE" \
  -d "redirect_uri=http://localhost:3000/callback" \
  -d "code_verifier=CODE_VERIFIER" \
  -d "client_id=CLIENT_ID"
```

Response:
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "...",
  "scope": "mcp:tools:read mcp:tools:execute"
}
```

### 5. Call MCP Tool

```bash
curl -X POST http://localhost:8000/mcp/tools/call \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
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
  }'
```

## Available MCP Tools

1. **get_weather** - Get weather information for a location
   - Parameters: `location` (required), `units` (optional)

2. **list_files** - List files in a directory
   - Parameters: `path` (required), `pattern` (optional)

3. **get_user_profile** - Get authenticated user's profile
   - Parameters: none

## Testing

Run the end-to-end test:

```bash
# Start the server first
uvicorn app.main:app

# In another terminal
python tests/test_flow.py
```

Or use pytest:

```bash
pip install pytest
pytest tests/
```

## Configuration

Environment variables (see `docker-compose.yml` for defaults):

- `JWT_SECRET_KEY` - Secret key for JWT signing
- `JWT_ALGORITHM` - JWT algorithm (default: HS256)
- `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` - Access token lifetime (default: 60)
- `SERVER_URL` - Server base URL (default: http://localhost:8000)
- `DEBUG` - Debug mode (default: true)
- `LOG_LEVEL` - Logging level (default: INFO)

## Architecture

```
server/
├── app/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration
│   ├── models.py            # Pydantic models
│   ├── storage.py           # In-memory storage
│   ├── oauth/
│   │   ├── metadata.py      # RFC 8414 & 9728 metadata
│   │   ├── dcr.py           # RFC 7591 - Dynamic Client Registration
│   │   ├── authorize.py     # Authorization endpoint
│   │   ├── token.py         # Token endpoint
│   │   └── pkce.py          # PKCE utilities
│   └── mcp/
│       ├── protocol.py      # MCP JSON-RPC handler
│       └── tools.py         # Example MCP tools
├── tests/
│   └── test_flow.py         # End-to-end tests
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Standards Implemented

- [RFC 7591](https://datatracker.ietf.org/doc/html/rfc7591) - OAuth 2.0 Dynamic Client Registration Protocol
- [RFC 7636](https://datatracker.ietf.org/doc/html/rfc7636) - Proof Key for Code Exchange (PKCE)
- [RFC 8414](https://datatracker.ietf.org/doc/html/rfc8414) - OAuth 2.0 Authorization Server Metadata
- [RFC 9728](https://datatracker.ietf.org/doc/html/rfc9728) - OAuth 2.0 Protected Resource Metadata
- [MCP Authorization Specification](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization)

## Development Notes

- **In-Memory Storage**: This is a mock server using in-memory storage. Data is lost on restart.
- **Auto-Approval**: Authorization requests are automatically approved for testing convenience.
- **Mock Data**: MCP tools return mock data, not real services.
- **Production**: For production use, implement proper database storage, user authentication, and consent flows.

## License

MIT
