# Contributing to MCP OAuth DCR Reference Implementation

Thank you for your interest in contributing! This is a reference implementation and educational resource for the MCP Authorization Specification.

## 🎯 Project Goals

This project aims to:
1. **Demonstrate** Dynamic Client Registration + OAuth 2.0 for MCP
2. **Educate** developers on implementing MCP authorization
3. **Provide** a working reference implementation
4. **Document** when and how to use this approach

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- Git
- Basic understanding of OAuth 2.0
- Familiarity with MCP (Model Context Protocol)

### Development Setup

```bash
# Clone the repository
git clone https://github.com/kgang/superdynamic.git
cd superdynamic

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r server/requirements.txt

# Run tests to verify setup
python test_client.py
cd server && python tests/test_flow.py
```

## 🔧 Development Workflow

### Running the Server Locally

```bash
# Option 1: Using the helper script
cd server
./run.sh

# Option 2: Direct uvicorn
cd server
uvicorn app.main:app --reload

# Option 3: Docker
cd server
docker compose up --build
```

### Running Tests

```bash
# Run all tests
pytest tests/test_client.py           # Client tests
pytest tests/server/test_flow.py      # Server tests

# Start server first for tests
cd server
uvicorn app.main:app --port 8000 &
cd ..
pytest tests/test_client.py
```

### Code Style

- **Python**: Follow PEP 8 guidelines
- **Imports**: Standard library first, then third-party, then local
- **Docstrings**: Use clear, concise docstrings for classes and functions
- **Type hints**: Add type hints where they improve clarity
- **Comments**: Explain "why" not "what"

## 📝 Types of Contributions

### 1. Bug Fixes

**Before submitting:**
- Verify the bug exists in the latest version
- Check if an issue already exists
- Write a test that reproduces the bug
- Fix the bug and ensure the test passes

**Process:**
1. Create an issue describing the bug
2. Fork the repository
3. Create a branch: `fix/description-of-bug`
4. Make your changes
5. Run tests
6. Submit a pull request

### 2. New MCP Tools

Adding new example MCP tools is a great contribution!

**Location**: `server/app/mcp/tools.py`

**Template**:
```python
@router.post("/call")
async def call_tool(request: ToolCallRequest, user_id: str = Depends(get_current_user)):
    """Handle tool invocation with Bearer token authentication."""

    if request.name == "your_tool_name":
        # Your tool implementation
        return ToolCallResponse(
            jsonrpc="2.0",
            id=request.id,
            result={
                "message": "Description of what happened",
                "data": {
                    # Your tool's response data
                }
            }
        )
```

**Requirements**:
- Must require authentication (use `user_id` from token)
- Should return meaningful data
- Include clear description
- Add to `list_tools()` endpoint
- Update documentation

### 3. Documentation Improvements

Documentation improvements are always welcome:

- Fix typos or unclear explanations
- Add more examples
- Improve API documentation
- Translate documentation
- Add diagrams or visualizations

**Documentation files**:
- `README.md` - Main overview and quick start
- `ARCHITECTURE.md` - Design decisions and use cases
- `security/` - Security audits for server and client
- `FLOW_DIAGRAM.md` - Visual walkthrough
- `server/README.md` - Server-specific docs

### 4. Test Coverage

Help improve test coverage:

**Areas needing tests**:
- Edge cases in OAuth flow
- Error handling scenarios
- Multiple concurrent clients
- Token expiration edge cases
- PKCE parameter validation

**Test locations**:
- `test_client.py` - Client integration tests
- `server/tests/test_flow.py` - Server flow tests

### 5. Security Enhancements

Security improvements are important but should be discussed first:

1. Open an issue describing the security concern
2. Discuss potential solutions
3. Implement after agreement
4. Include tests demonstrating the fix

**Note**: This is a reference implementation, not production-ready. Security improvements should balance educational clarity with production best practices.

## 🔍 Pull Request Process

### Before Submitting

1. **Run all tests**:
   ```bash
   pytest tests/test_client.py
   pytest tests/server/test_flow.py
   # Or run all tests at once
   pytest tests/
   ```

2. **Check code quality**:
   ```bash
   # No syntax errors
   python -m py_compile client.py
   python -m py_compile server/app/**/*.py
   ```

3. **Update documentation** if needed

4. **Add tests** for new functionality

### PR Guidelines

**Title**: Clear, concise description
- ✅ `Add calendar integration MCP tool`
- ✅ `Fix token refresh race condition`
- ❌ `Updates`
- ❌ `Fixed bug`

**Description should include**:
- What changed and why
- Link to related issue (if applicable)
- Test results
- Screenshots/examples (if applicable)

**Commit messages**:
```bash
# Good
Add support for OAuth scope customization

This allows clients to request specific scopes during registration,
enabling more granular permission control.

# Avoid
update stuff
fix
```

### Review Process

1. Automated tests must pass (GitHub Actions)
2. Code review by maintainer
3. Address feedback
4. Merge when approved

## 🏗️ Project Structure

```
├── client.py                 # MCP OAuth client (main contribution area)
├── tests/                   # Test suite
│   ├── test_client.py      # Client tests
│   └── server/             # Server tests
├── server/
│   ├── app/
│   │   ├── oauth/          # OAuth endpoints (DCR, authorize, token)
│   │   └── mcp/            # MCP protocol (tools, protocol handling)
│   └── tests/              # Server tests
├── security/                # Security audits and assessments
│   ├── components/         # Component-specific audits
│   │   ├── SERVER_SECURITY_AUDIT.md
│   │   └── CLIENT_SECURITY_AUDIT.md
│   └── complete-audits/    # System-wide assessments
│       ├── IMPLEMENTATION_SUMMARY.md
│       ├── LLM_CODE_ASSESSMENT_FRAMEWORK.md
│       ├── VERIFIED_CRITICAL_FINDINGS.md
│       └── ASSESSMENT_SUMMARY.md
├── ARCHITECTURE.md          # Design documentation
└── FLOW_DIAGRAM.md          # Authorization flow visualization
```

## 🐛 Reporting Issues

### Bug Reports

Include:
- **Python version**: `python3 --version`
- **Operating system**: macOS, Linux, Windows
- **Error message**: Full traceback
- **Steps to reproduce**: Minimal example
- **Expected vs actual behavior**

### Feature Requests

Include:
- **Use case**: Why is this needed?
- **Proposed solution**: How would it work?
- **Alternatives considered**: Other approaches?
- **Impact**: Who benefits?

## 📚 Resources

- [MCP Authorization Spec](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization)
- [RFC 7591 - Dynamic Client Registration](https://datatracker.ietf.org/doc/html/rfc7591)
- [RFC 7636 - PKCE](https://datatracker.ietf.org/doc/html/rfc7636)
- [OAuth 2.0 Framework](https://datatracker.ietf.org/doc/html/rfc6749)

## 🤝 Code of Conduct

Be respectful and constructive:
- Welcome newcomers
- Assume good intent
- Provide helpful feedback
- Focus on the code, not the person

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## ❓ Questions?

- Open an issue for general questions
- Tag issues with `question` label
- Check existing issues and documentation first

---

Thank you for contributing to MCP OAuth DCR! 🎉
