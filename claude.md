# MCP OAuth DCR Client - Development Session Notes

**Project**: MCP Client with Dynamic Client Registration and OAuth 2.0 Flow
**Branch**: `claude/mcp-oauth-dcr-client-011CUmhgyCzRnebRLuNKcNy9`
**Started**: 2025-11-03

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
