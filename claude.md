# MCP OAuth DCR Client - Development Session Notes

**Project**: MCP Client with Dynamic Client Registration and OAuth 2.0 Flow
**Branch**: `claude/mcp-dcr-oauth-client-011CUmiGUsriSF3EmFCiCEdB`
**Started**: 2025-11-03

---

## Session 2: Mock MCP Server Implementation (2025-11-03)

### DECISION: Build Complete Mock Server
- **Chose**: Build full-featured mock MCP server from scratch using FastAPI
- **Over**: Using existing libraries or minimal implementation
- **Rationale**:
  - No existing MCP servers with DCR support found
  - Full control over implementation for testing
  - Better understanding of protocol mechanics
  - Can serve as reference implementation

### DECISION: FastAPI Framework
- **Chose**: FastAPI for web framework
- **Over**: Flask, Django, or pure Python
- **Rationale**:
  - Built-in async support
  - Automatic OpenAPI documentation
  - Pydantic integration for validation
  - Modern, clean API design
  - Industry standard for API development

### DECISION: In-Memory Storage
- **Chose**: Simple Python dictionaries for storage
- **Over**: Database (SQLite, PostgreSQL, Redis)
- **Rationale**:
  - Simplifies deployment and testing
  - No external dependencies
  - Acceptable data loss for mock server
  - Keeps within 5-package constraint

### DECISION: JWT for Access Tokens
- **Chose**: Self-contained JWT tokens
- **Over**: Opaque tokens with database lookup
- **Rationale**:
  - Stateless validation
  - Industry standard (python-jose)
  - Simpler architecture
  - No revocation needed for mock server

### RESOURCE: MCP Authorization Research
- Found Azure-Samples/remote-mcp-webapp-python-auth-oauth as reference
- RFC 9728 (Protected Resource Metadata) critical for MCP discovery
- RFC 7591 (DCR) has minimal required fields (only redirect_uris for auth code flow)
- PKCE with S256 is standard security practice

### PROGRESS: Server Implementation Complete

**Completed**:
- ✅ Complete project structure with modular design
- ✅ OAuth 2.0 Authorization Server implementation
  - RFC 7591 Dynamic Client Registration endpoint
  - RFC 7636 PKCE implementation (generation & validation)
  - Authorization endpoint with auto-approval
  - Token endpoint with authorization_code and refresh_token grants
  - RFC 8414 Authorization Server Metadata endpoint
  - RFC 9728 Protected Resource Metadata endpoint
- ✅ MCP Protocol Implementation
  - JSON-RPC 2.0 handler
  - initialize, tools/list, tools/call methods
  - Bearer token authentication middleware
  - WWW-Authenticate headers for 401 responses
- ✅ Three example MCP tools
  - get_weather: Mock weather data
  - list_files: Mock file system
  - get_user_profile: User info from token claims
- ✅ Docker support
  - Idiomatic Dockerfile with health checks
  - docker-compose.yml with environment variables
  - Hot reload support for development
- ✅ Testing infrastructure
  - End-to-end test demonstrating full flow
  - PKCE generation utilities
  - Test covers all 9 steps of the flow
- ✅ Documentation
  - Comprehensive README with examples
  - API documentation via FastAPI auto-docs
  - Helper scripts (run.sh)

**Dependencies Used** (6 packages, within constraint):
1. fastapi - Web framework
2. uvicorn[standard] - ASGI server
3. pydantic - Data validation
4. pydantic-settings - Configuration management
5. python-jose[cryptography] - JWT handling
6. httpx - HTTP client for testing

**Files Created** (22 files):
```
server/
├── app/
│   ├── __init__.py, config.py, main.py, models.py, storage.py
│   ├── oauth/: metadata.py, dcr.py, authorize.py, token.py, pkce.py
│   └── mcp/: protocol.py, tools.py
├── tests/: test_flow.py
├── Dockerfile, docker-compose.yml, requirements.txt
├── README.md, .gitignore, run.sh
```

### ASSUMPTION: HTTP Transport for MCP
- **Assumed**: MCP over HTTP/REST (not SSE or WebSocket)
- **Rationale**: Simpler for initial implementation, aligns with OAuth redirects
- **Needs Validation**: May need to support SSE for real MCP clients

### NEXT STEPS
1. ✅ ~~Implement mock MCP server~~ **COMPLETE**
2. Test server locally to verify all endpoints work
3. Design and implement Python client
4. Test complete end-to-end flow
5. Document learnings and POV on DCR + OAuth with MCP

---

## Session 1: Project Initialization (2025-11-03)

### DECISION: Project Structure
- Created `requirements.md` to document technical requirements and constraints
- Created this `claude.md` file for session tracking and decision log
- **Rationale**: Clear documentation foundation before diving into implementation

### ASSUMPTION: Technical Approach
- Will need to implement or find a mock MCP server that supports DCR + OAuth
- May need to build both client and server components since spec is new
- **Needs Validation**: Availability of existing MCP servers with auth support

### RESOURCE: Key Specifications
- [MCP Authorization Spec](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization)
- [RFC 7591 - DCR](https://datatracker.ietf.org/doc/html/rfc7591)
- [RFC 7636 - PKCE](https://datatracker.ietf.org/doc/html/rfc7636)
- [RFC 6749 - OAuth 2.0](https://datatracker.ietf.org/doc/html/rfc6749)

### NEXT STEPS
1. Research MCP Authorization spec in detail
2. Identify or build mock server with DCR support
3. Design client architecture
4. Implement DCR registration flow
5. Implement OAuth 2.0 + PKCE flow
6. Implement MCP tool invocation
7. Test end-to-end flow

---

## Template for Future Sessions

### BLOCKING
- [ ] Issue description
- [ ] What would unblock

### DECISION
- Chose X over Y because Z

### ASSUMPTION
- Assumed X, needs validation

### RESOURCE
- Useful doc/example at [URL]

### PROGRESS
- What was completed
- What's in progress
- What's next

---

## Questions to Answer During Development

1. **Architecture**: Should we build a standalone mock server or embed it?
2. **OAuth Server**: Use existing OAuth library/server or build minimal implementation?
3. **Token Storage**: How to handle token persistence between runs?
4. **Error Handling**: What failure modes are most important to handle gracefully?
5. **Testing**: Unit tests vs integration tests vs manual testing?
6. **Use Cases**: When is DCR + OAuth appropriate vs other auth methods?

---

## Implementation Checklist

### Phase 1: Research & Design
- [ ] Deep dive into MCP Authorization spec
- [ ] Understand DCR registration endpoint requirements
- [ ] Map out OAuth 2.0 + PKCE flow in MCP context
- [ ] Design client architecture
- [ ] Identify dependencies (max 5 packages)

### Phase 2: Server Setup
- [ ] Implement or configure mock MCP server
- [ ] Add DCR registration endpoint
- [ ] Add OAuth authorization endpoint
- [ ] Add OAuth token endpoint
- [ ] Add at least 2 MCP tools for testing

### Phase 3: Client Implementation
- [ ] CLI argument parsing
- [ ] DCR registration logic
- [ ] PKCE code challenge/verifier generation
- [ ] OAuth authorization flow (with browser callback)
- [ ] Token exchange
- [ ] Token refresh (if time permits)
- [ ] MCP tool invocation with auth headers

### Phase 4: Testing & Documentation
- [ ] End-to-end flow testing
- [ ] Error case handling
- [ ] README with setup/usage instructions
- [ ] Architecture documentation
- [ ] "When to use" guidance

---

## POV Development: When to Use DCR + OAuth with MCP

*This section will be populated as understanding develops*

### Appropriate Use Cases
- TBD

### Not Recommended For
- TBD

### Trade-offs
- TBD

---

## Notes on LLM-Driven Development

*Observations about using Claude Code for this project*

- TBD
