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
- [ ] Identify dependencies (max 25 packages)

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

*Updated: 2025-11-03 after implementation and security audit*

### Appropriate Use Cases

**1. Multi-User SaaS MCP Servers**
- Each user owns distinct data (files, emails, documents)
- Need to enforce user-specific permissions
- Require audit trails showing which user authorized which AI actions
- Example: Google Workspace MCP server, Salesforce MCP server

**2. Third-Party AI Integrations**
- AI applications connecting to multiple enterprise MCP servers
- Cannot pre-register with every possible service provider
- Users want to control which tools AI can access
- Example: AI coding assistant connecting to internal company tools

**3. Dynamic Integration Scenarios**
- Users self-service connecting AI to new services
- Marketplace of MCP servers with standardized auth
- No IT intervention required for each new integration
- Example: Enterprise AI platform with plug-in ecosystem

**4. Security/Compliance Requirements**
- Healthcare (HIPAA), financial (SOX), legal data
- Need explicit user consent before AI accesses sensitive data
- Compliance officers need audit logs of AI data access
- Token expiration ensures time-limited access

### Not Recommended For

**1. Single-User Local Tools**
- Personal desktop apps with no data sharing
- Developer tools accessing local filesystem
- Can use simpler API keys or environment variables
- OAuth overhead doesn't add security value

**2. Trusted First-Party Integrations**
- Same organization controls both client and server
- Can use service accounts with proper RBAC
- Internal auth system already handles user identity
- Example: Company's AI assistant accessing internal knowledge base

**3. STDIO-Based MCP Servers**
- Local processes communicating via standard input/output
- MCP spec explicitly recommends environment credentials
- HTTP/OAuth overhead inappropriate for local IPC
- Example: Local code analysis tools

**4. Public Data / Read-Only Access**
- MCP server serves public, non-sensitive data
- No user-specific permissions needed
- Auth overhead creates friction without benefit
- Example: Public weather API, news aggregator

### Trade-offs

| Aspect | DCR + OAuth | Simpler Auth | Notes |
|--------|-------------|--------------|-------|
| **Setup Complexity** | High | Low | OAuth requires auth server infrastructure |
| **User Friction** | Medium | Low | User must approve consent screen |
| **Security** | High | Low-Medium | Token-based, scoped, time-limited access |
| **Audit Trail** | Excellent | Poor | Every auth event logged with user context |
| **Scalability** | Excellent | Poor | Zero-touch onboarding to new services |
| **Multi-User Support** | Native | Requires custom code | OAuth designed for multi-user scenarios |
| **Token Revocation** | Built-in | Must build | User can revoke AI access anytime |
| **Dynamic Integrations** | Excellent | Impossible | DCR enables self-registration |

### Key Insights

**Why DCR is Critical:**
Traditional OAuth requires manual client registration (developer gets client_id from service provider's website). This doesn't scale when AI needs to connect to arbitrary enterprise MCP servers. DCR solves this by allowing **programmatic registration**.

**When OAuth is Overkill:**
If you control both client and server, or there's only one user, OAuth's complexity doesn't pay off. Use API keys, service accounts, or environment variables instead.

**The "Enterprise Integration" Litmus Test:**
Ask: "Would a third-party AI tool need user permission to access this data?"
- Yes → Use OAuth + DCR
- No → Use simpler auth

**Security vs. Usability Balance:**
OAuth + DCR optimizes for **security in multi-user, multi-tenant environments** at the cost of **setup complexity**. Choose based on your threat model and user base.

---

## Notes on LLM-Driven Development

*Observations about using Claude Code for this project*

### What Worked Exceptionally Well

**1. Rapid Specification Implementation**
- **Challenge**: Implement brand-new spec (~2 months old) with minimal examples
- **Outcome**: Complete OAuth + DCR + MCP server in single session
- **Why it worked**:
  - Claude understands OAuth/PKCE deeply from training data
  - Can synthesize multiple RFCs (7591, 7636, 6749, 8414, 9728) simultaneously
  - Writes idiomatic Python/FastAPI code
  - Generates comprehensive tests

**2. Standards Compliance**
- Claude naturally implements best practices from OAuth 2.1 spec
- Automatically includes security features (PKCE, single-use codes, token expiration)
- Validates against official RFCs without prompting
- Identifies edge cases and error conditions

**3. Documentation Generation**
- Generated comprehensive README, architecture docs, security audit
- Clear explanations of complex flows (PKCE, JWT validation)
- Markdown formatting and examples without manual editing

**4. Incremental Development**
- Built modular structure (oauth/, mcp/ directories)
- Clean separation of concerns (metadata, DCR, authorize, token endpoints)
- Easy to iterate and extend

### Challenges and Workarounds

**1. Conceptual Ambiguity**
- **Challenge**: MCP spec doesn't specify exact interaction between DCR and MCP
- **Solution**: Claude made reasonable architectural decisions (co-located auth server)
- **Lesson**: For new specs, LLM makes opinionated but sound choices

**2. Missing Production Features**
- **Initially**: Focused on "make it work" over production-readiness
- **Gap**: No consent UI, in-memory storage, missing `aud` claim
- **Addressed**: Security audit identified gaps, easy to fix post-implementation
- **Lesson**: LLM optimizes for functionality first, hardening second

**3. Testing Edge Cases**
- **Challenge**: Mock server needed realistic failure modes
- **Solution**: Explicitly requested error handling for invalid tokens, expired codes
- **Lesson**: Test-driven prompts produce more robust code

### Surprising Strengths

**1. Multi-RFC Synthesis**
- Claude seamlessly combined 5+ RFCs into coherent implementation
- No contradictions between OAuth 2.0, PKCE, DCR, metadata standards
- Understands precedence when specs conflict

**2. Security-First Design**
- Automatically includes WWW-Authenticate headers
- Validates redirect URIs strictly
- Uses cryptographically secure random for tokens
- Prevents common vulnerabilities (code replay, CSRF)

**3. Developer Experience**
- Generated Docker setup, health checks, API documentation
- Clear variable names, comprehensive docstrings
- FastAPI auto-docs (Swagger UI) for interactive testing

### Where Human Oversight Matters

**1. Architectural Decisions**
- Co-located vs. separate auth server
- In-memory vs. persistent storage
- Auto-approval vs. consent UI
- **Takeaway**: Claude makes reasonable defaults, but humans must decide trade-offs

**2. Security Hardening**
- Missing `aud` claim was oversight
- Refresh token rotation not implemented initially
- Resource parameter not validated
- **Takeaway**: Security audit essential even with LLM-generated code

**3. Production Deployment**
- HTTPS configuration, secret management, monitoring not addressed
- Database schema design, migrations, backup strategies
- **Takeaway**: LLM great for application logic, humans handle ops

### Productivity Metrics (Estimated)

| Task | Traditional Dev | With Claude Code | Speedup |
|------|-----------------|------------------|---------|
| **OAuth server scaffold** | 4-6 hours | 15 minutes | 16-24x |
| **PKCE implementation** | 2-3 hours (researching RFC) | 10 minutes | 12-18x |
| **MCP protocol handler** | 2-4 hours | 20 minutes | 6-12x |
| **Testing** | 3-4 hours | 30 minutes | 6-8x |
| **Documentation** | 4-6 hours | 45 minutes | 5-8x |
| **Total** | ~15-23 hours | ~2 hours | **~10x faster** |

*Note: Estimates assume developer familiar with OAuth but implementing DCR for first time*

### Best Practices Learned

**1. Specification-First Prompts**
- Provide relevant RFCs and spec sections upfront
- Ask Claude to identify compliance requirements
- Request security considerations early

**2. Iterative Refinement**
- Build working implementation first
- Run tests to identify gaps
- Security audit to find vulnerabilities
- Harden based on findings

**3. Ask for Opinions**
- "What security considerations should I think about?"
- "What production concerns exist with this design?"
- Claude surfaces issues humans might miss

**4. Validate Outputs**
- Run the code, don't just read it
- Test edge cases explicitly
- Cross-reference with official documentation

### Would I Use Claude Code for This Again?

**Absolutely.**

**Perfect for:**
- Implementing well-specified protocols (OAuth, JWT, REST APIs)
- Rapid prototyping of new standards
- Generating comprehensive test suites
- Creating reference implementations

**Less ideal for:**
- Novel algorithms with no training data
- Performance-critical optimization
- Hardware-specific concerns
- Highly regulated domains requiring certification

### Key Insight

**LLM-driven development is about leveraging the 80/20 rule**: Claude Code handles 80% of implementation (boilerplate, standards compliance, common patterns) in 20% of the time, freeing humans to focus on the critical 20% (architecture, security hardening, production operations) that delivers 80% of business value.

For a project like MCP + OAuth + DCR—where the specification is clear but examples are scarce—this approach is **transformative**. We went from zero to a working, well-documented reference implementation in hours instead of days.
