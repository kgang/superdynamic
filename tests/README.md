# Test Suite

Comprehensive tests for the MCP OAuth DCR implementation.

## Structure

```
tests/
├── conftest.py                      # Pytest fixtures and configuration
├── test_client.py                   # Client integration tests
├── test_security_vulnerabilities.py # Security vulnerability tests
└── server/                          # Server-specific tests
    └── test_flow.py                # Server OAuth flow tests
```

## Running Tests

### All Tests
```bash
pytest tests/
```

### Specific Test Files
```bash
# Client integration tests
python tests/test_client.py

# Server functional tests
python tests/server/test_flow.py

# Security vulnerability tests
pytest tests/test_security_vulnerabilities.py -v
```

### By Marker
```bash
# Run only security tests
pytest -m security

# Run only integration tests
pytest -m integration

# Run only unit tests
pytest -m unit
```

## Test Categories

### Integration Tests (`test_client.py`)
- Full OAuth flow testing
- Client registration (DCR)
- Token exchange
- MCP tool invocation
- Token refresh
- Multi-client lifecycle

**Prerequisites**: Server must be running at http://localhost:8000

### Server Tests (`server/test_flow.py`)
- OAuth server endpoints
- Dynamic Client Registration
- PKCE validation
- Token issuance
- MCP protocol

**Prerequisites**: Server must be running

### Security Tests (`test_security_vulnerabilities.py`)
Tests for critical vulnerabilities identified in security audit:

1. **Authorization Code Race Condition** - TOCTOU vulnerability
2. **DateTime Timezone Mismatch** - Client miscalculates token expiration
3. **Missing Resource Parameter** - MCP spec violation
4. **PKCE Implementation** - Cryptographic correctness
5. **Network Error Handling** - Error handling gaps

**Note**: These tests are currently set to **document vulnerabilities**.
When fixes are implemented, update assertions to verify fixes work.

## Configuration

### pytest.ini
Main pytest configuration:
- Test discovery patterns
- Markers registration
- Output configuration
- Coverage settings (if enabled)

### conftest.py
Shared fixtures:
- `server_url` - Base URL for test server
- `server_health_check` - Verify server is running
- `client_factory` - Create test OAuth clients
- `pkce_params` - Generate PKCE parameters
- `auth_code_factory` - Obtain authorization codes

## Continuous Integration

Tests run automatically on GitHub Actions:
- Python 3.10, 3.11, 3.12
- Both native and Docker deployments
- See `.github/workflows/test.yml`

## Writing New Tests

### Standard Format
```python
import pytest

@pytest.mark.integration
def test_my_feature(server_url, server_health_check):
    """Test description."""
    # Setup
    client = create_client()

    # Execute
    result = client.do_something()

    # Assert
    assert result is not None
    assert result["status"] == "success"
```

### Using Fixtures
```python
def test_with_client(client_factory, pkce_params):
    """Use fixtures for common setup."""
    client = client_factory("My Test Client")

    assert client["client_id"] is not None
    assert len(pkce_params["verifier"]) >= 43
```

## Test Markers

- `@pytest.mark.security` - Security vulnerability tests
- `@pytest.mark.integration` - Integration tests (require server)
- `@pytest.mark.unit` - Unit tests (no external dependencies)
- `@pytest.mark.slow` - Slow-running tests

## Troubleshooting

### Server Not Running
```bash
# Start server
cd server && docker-compose up

# Or run natively
cd server && python -m uvicorn app.main:app
```

### Import Errors
```bash
# Install dependencies
pip install -r requirements.txt
pip install -r server/requirements.txt
pip install pytest pytest-asyncio
```

### Port Conflicts
If port 8000 is in use:
```bash
# Check what's using the port
lsof -i :8000

# Kill the process
kill -9 <PID>
```

## Coverage (Optional)

To run tests with coverage:
```bash
# Install coverage
pip install pytest-cov

# Run with coverage
pytest --cov=client --cov=server/app --cov-report=html

# View report
open htmlcov/index.html
```

## Related Documentation

- [Security Audits](../security/) - Detailed security analysis
- [Architecture](../ARCHITECTURE.md) - System design
- [README](../README.md) - Main project documentation
