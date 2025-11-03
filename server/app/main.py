"""
MCP OAuth DCR Server - Main Application

A mock Model Context Protocol server implementing:
- OAuth 2.0 Authorization Server with Dynamic Client Registration (RFC 7591)
- Authorization Code Flow with PKCE (RFC 7636)
- Protected Resource Metadata (RFC 9728)
- MCP tool execution with OAuth authentication
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.config import settings
from app.oauth import metadata, dcr, authorize, token
from app.mcp import protocol

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="MCP OAuth DCR Server",
    description=(
        "Mock MCP server with OAuth 2.0 Authorization Server, "
        "Dynamic Client Registration, and PKCE support"
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware for browser-based clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Exception Handlers
# ============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_server_error",
            "error_description": str(exc) if settings.DEBUG else "An internal error occurred"
        }
    )


# ============================================================================
# Include Routers
# ============================================================================

# OAuth metadata endpoints (RFC 8414, RFC 9728)
app.include_router(metadata.router, tags=["OAuth Metadata"])

# OAuth endpoints
app.include_router(dcr.router, tags=["Dynamic Client Registration"])
app.include_router(authorize.router, tags=["OAuth Authorization"])
app.include_router(token.router, tags=["OAuth Token"])

# MCP protocol endpoints
app.include_router(protocol.router, tags=["MCP Protocol"])


# ============================================================================
# Root Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint with server information and links."""
    return {
        "name": "MCP OAuth DCR Server",
        "version": "0.1.0",
        "description": "Mock MCP server with OAuth 2.0 and Dynamic Client Registration",
        "endpoints": {
            "metadata": {
                "authorization_server": f"{settings.SERVER_URL}/.well-known/oauth-authorization-server",
                "protected_resource": f"{settings.SERVER_URL}/.well-known/oauth-protected-resource"
            },
            "oauth": {
                "register": f"{settings.SERVER_URL}/oauth/register",
                "authorize": f"{settings.SERVER_URL}/oauth/authorize",
                "token": f"{settings.SERVER_URL}/oauth/token"
            },
            "mcp": {
                "initialize": f"{settings.SERVER_URL}/mcp/initialize",
                "tools_list": f"{settings.SERVER_URL}/mcp/tools/list",
                "tools_call": f"{settings.SERVER_URL}/mcp/tools/call"
            },
            "documentation": {
                "openapi": f"{settings.SERVER_URL}/docs",
                "redoc": f"{settings.SERVER_URL}/redoc"
            }
        },
        "standards": [
            "RFC 7591 - OAuth 2.0 Dynamic Client Registration",
            "RFC 7636 - Proof Key for Code Exchange (PKCE)",
            "RFC 8414 - OAuth 2.0 Authorization Server Metadata",
            "RFC 9728 - OAuth 2.0 Protected Resource Metadata",
            "MCP Authorization Specification"
        ]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "service": "mcp-oauth-dcr-server",
        "version": "0.1.0"
    }


# ============================================================================
# Startup/Shutdown Events
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Log startup information."""
    logger.info("=" * 60)
    logger.info("MCP OAuth DCR Server Starting")
    logger.info("=" * 60)
    logger.info(f"Server URL: {settings.SERVER_URL}")
    logger.info(f"Debug Mode: {settings.DEBUG}")
    logger.info(f"Log Level: {settings.LOG_LEVEL}")
    logger.info("=" * 60)
    logger.info("OAuth Endpoints:")
    logger.info(f"  - Registration: {settings.SERVER_URL}/oauth/register")
    logger.info(f"  - Authorize: {settings.SERVER_URL}/oauth/authorize")
    logger.info(f"  - Token: {settings.SERVER_URL}/oauth/token")
    logger.info("=" * 60)
    logger.info("MCP Endpoints:")
    logger.info(f"  - Initialize: {settings.SERVER_URL}/mcp/initialize")
    logger.info(f"  - Tools List: {settings.SERVER_URL}/mcp/tools/list")
    logger.info(f"  - Tools Call: {settings.SERVER_URL}/mcp/tools/call")
    logger.info("=" * 60)
    logger.info("Documentation:")
    logger.info(f"  - OpenAPI Docs: {settings.SERVER_URL}/docs")
    logger.info(f"  - ReDoc: {settings.SERVER_URL}/redoc")
    logger.info("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """Log shutdown information."""
    logger.info("MCP OAuth DCR Server Shutting Down")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
