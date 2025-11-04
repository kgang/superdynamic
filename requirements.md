# MCP OAuth DCR Client - Requirements

## Overview

Build a Model Context Protocol (MCP) client that implements Dynamic Client Registration (DCR) per RFC 7591 and OAuth 2.0 Authorization Code Flow with PKCE (RFC 7636) to demonstrate the MCP Authorization Specification.

## Background

The [MCP Authorization Spec](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization) introduces authorization capabilities to the Model Context Protocol. This project focuses on Dynamic Client Registration (DCR), which enables clients to self-register with MCP servers and establish OAuth-based authenticated sessions.

### Key Challenges
- New specification (~2 months old) with minimal reference implementations
- Requires understanding the full auth callback cycle in MCP context
- Intersection of modern identity/SSO best practices with MCP protocol

## Use Case

Build a client that can:
1. Self-register to an MCP server using DCR
2. Use the negotiated `client_id` to establish OAuth connection for a user
3. Successfully invoke authenticated MCP tools

## Technical Requirements

### Core Features (Implemented)
- Dynamic Client Registration (RFC 7591) implementation
- OAuth 2.0 Authorization Code Flow with PKCE (RFC 7636)
- Mock MCP server for testing
- Multiple authenticated MCP tool invocations
- Simple CLI interface: `python client.py --server-url <url>`
- OAuth token refresh handling
- Clear error messages for authentication failures
- Configuration support via CLI arguments and JSON storage
- Comprehensive documentation of when/how to use this approach
- Token storage/caching between sessions
- Support for multiple MCP servers (multi-client lifecycle)

## Technical Constraints

- **Language**: Python 3.10+
- **Dependencies**: Maximum 5 PyPI packages
- **APIs**: No proprietary APIs without mock fallback
- **Portability**: Should run on standard Python environment

## Deliverables

1. **Working Client**: Python-based MCP client with DCR + OAuth
2. **Mock Server**: Test server implementing MCP auth spec (if needed)
3. **Documentation**:
   - Setup and usage instructions (README.md)
   - Architecture decisions and approach (claude.md)
   - Clear POV on when/how to use this approach
4. **Proof of Concept**: Easily runnable demo showing end-to-end flow

## Success Criteria

All requirements have been successfully implemented:

- Client successfully registers via DCR with server
- Client obtains OAuth authorization from user
- Client exchanges authorization code for access token (with PKCE)
- Client makes authenticated MCP tool calls
- Complete flow is documented and reproducible
- Clear understanding of when this approach is appropriate

See `client.py` for the complete implementation and `tests/test_client.py` for integration tests.

## Key Standards Referenced

- [RFC 7591](https://datatracker.ietf.org/doc/html/rfc7591) - OAuth 2.0 Dynamic Client Registration Protocol
- [RFC 7636](https://datatracker.ietf.org/doc/html/rfc7636) - Proof Key for Code Exchange (PKCE)
- [RFC 6749](https://datatracker.ietf.org/doc/html/rfc6749) - OAuth 2.0 Authorization Framework
- [MCP Authorization Spec](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization)

## Development Approach

Built using Claude Code to explore LLM-driven development workflows and demonstrate:
- Rapid prototyping of new specifications
- Integration of multiple complex standards
- Clear documentation and decision tracking
