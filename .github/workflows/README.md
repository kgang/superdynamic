# GitHub Actions Workflows

## test.yml - MCP Server Tests

Automated testing workflow for the MCP OAuth DCR server.

### Triggers

- **Push**: Runs on pushes to `main` and any `claude/**` branches
- **Pull Request**: Runs on PRs targeting `main`

### Jobs

#### 1. `test` - Python Matrix Tests

Tests the server across multiple Python versions using direct Python execution.

**Python Versions Tested:**
- 3.10
- 3.11
- 3.12

**Steps:**
1. Checkout code
2. Set up Python environment
3. Cache pip packages for faster builds
4. Install dependencies from `server/requirements.txt`
5. Start MCP server in background with environment variables
6. Wait for server to be ready (health check with retry)
7. Run functional test suite (`server/tests/test_flow.py`)
8. Show server logs if tests fail
9. Stop server gracefully
10. Upload server logs as artifacts (retained for 7 days)

**Environment Variables:**
```bash
JWT_SECRET_KEY: test-secret-key-for-ci-cd-testing-only
JWT_ALGORITHM: HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES: 60
SERVER_URL: http://localhost:8000
DEBUG: true
LOG_LEVEL: INFO
```

#### 2. `docker-test` - Docker Integration Test

Tests the server using Docker Compose to validate containerized deployment.

**Steps:**
1. Checkout code
2. Build Docker image
3. Start server with `docker-compose up -d`
4. Wait for container health check
5. Set up Python for test runner
6. Install test dependencies
7. Run functional tests against Dockerized server
8. Show Docker logs if tests fail
9. Stop and clean up Docker containers

### Artifacts

- **Server logs**: Uploaded for each Python version tested
  - Retention: 7 days
  - Name pattern: `server-logs-python-{version}`
  - Available in Actions tab → Workflow run → Artifacts
  - Uses `actions/upload-artifact@v4` for improved performance

### Monitoring

**Success Criteria:**
- ✅ All HTTP requests return expected status codes
- ✅ OAuth flow completes: DCR → Auth → Token → MCP tool call → Refresh
- ✅ PKCE validation passes
- ✅ JWT tokens validate correctly with audience claims
- ✅ MCP tools execute successfully with authentication

**Failure Scenarios:**
- ❌ Server fails to start within 60 seconds
- ❌ Health check endpoint unreachable
- ❌ Any assertion failure in test suite
- ❌ Docker build or container startup failure

### Local Testing

To run the same tests locally:

```bash
# Terminal 1: Start server
cd server
uvicorn app.main:app --reload

# Terminal 2: Run tests
cd server
python tests/test_flow.py
```

### Debugging Failed Runs

1. Check the **Run functional tests** step output for assertion details
2. Download **server-logs** artifact for detailed server-side errors
3. Review **Show server logs on failure** step for immediate context
4. For Docker failures, check **Show Docker logs on failure** step

### Performance

**Typical run time:**
- Python matrix test (single version): ~2-3 minutes
- Docker test: ~3-4 minutes
- Total workflow: ~5-7 minutes (jobs run in parallel)

**Caching:**
- Pip packages cached using `~/.cache/pip` directory
- Uses `actions/cache@v4` for improved performance
- Cache key: `${{ runner.os }}-pip-${{ hashFiles('server/requirements.txt') }}`
- Significantly reduces dependency installation time on subsequent runs

### Status Badge

Add this badge to your README.md to show test status:

```markdown
![Tests](https://github.com/kgang/superdynamic/actions/workflows/test.yml/badge.svg)
```

### Future Enhancements

Potential improvements:
- [ ] Add code coverage reporting (pytest-cov)
- [ ] Run security scanning (bandit, safety)
- [ ] Add linting (flake8, black, mypy)
- [ ] Performance benchmarking
- [ ] Multi-architecture Docker builds (amd64, arm64)
- [ ] Integration with external OAuth providers
- [ ] Nightly builds with extended test suite
