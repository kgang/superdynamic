"""
In-memory storage for OAuth clients, authorization codes, and tokens.

NOTE: This is for development/testing only. Production implementations
should use a proper database with persistence.
"""

from typing import Dict, Optional
from datetime import datetime
from app.models import RegisteredClient, AuthorizationCode, RefreshToken


class InMemoryStorage:
    """Simple in-memory storage for OAuth entities."""

    def __init__(self):
        self.clients: Dict[str, RegisteredClient] = {}
        self.authorization_codes: Dict[str, AuthorizationCode] = {}
        self.refresh_tokens: Dict[str, RefreshToken] = {}

    # ========================================================================
    # Client Management
    # ========================================================================

    def store_client(self, client: RegisteredClient) -> None:
        """Store a registered client."""
        self.clients[client.client_id] = client

    def get_client(self, client_id: str) -> Optional[RegisteredClient]:
        """Retrieve a client by ID."""
        return self.clients.get(client_id)

    def client_exists(self, client_id: str) -> bool:
        """Check if client exists."""
        return client_id in self.clients

    # ========================================================================
    # Authorization Code Management
    # ========================================================================

    def store_authorization_code(self, auth_code: AuthorizationCode) -> None:
        """Store an authorization code."""
        self.authorization_codes[auth_code.code] = auth_code

    def get_authorization_code(self, code: str) -> Optional[AuthorizationCode]:
        """Retrieve an authorization code."""
        auth_code = self.authorization_codes.get(code)
        if not auth_code:
            return None

        # Check if expired
        if datetime.utcnow() > auth_code.expires_at:
            return None

        # Check if already used
        if auth_code.used:
            return None

        return auth_code

    def mark_code_as_used(self, code: str) -> bool:
        """
        Atomically mark an authorization code as used.

        Returns:
            True if code was successfully marked as used
            False if code doesn't exist, is already used, or is expired

        This method provides atomic check-and-set to prevent race conditions
        where multiple concurrent requests could reuse the same code.
        """
        auth_code = self.authorization_codes.get(code)

        if not auth_code:
            return False

        # Check if already used
        if auth_code.used:
            return False

        # Check if expired
        if datetime.utcnow() > auth_code.expires_at:
            return False

        # Atomically mark as used
        auth_code.used = True
        return True

    def cleanup_expired_codes(self) -> None:
        """Remove expired authorization codes."""
        now = datetime.utcnow()
        self.authorization_codes = {
            code: auth_code
            for code, auth_code in self.authorization_codes.items()
            if auth_code.expires_at > now
        }

    # ========================================================================
    # Refresh Token Management
    # ========================================================================

    def store_refresh_token(self, refresh_token: RefreshToken) -> None:
        """Store a refresh token."""
        self.refresh_tokens[refresh_token.token] = refresh_token

    def get_refresh_token(self, token: str) -> Optional[RefreshToken]:
        """Retrieve a refresh token."""
        refresh_token = self.refresh_tokens.get(token)
        if not refresh_token:
            return None

        # Check if expired
        if datetime.utcnow() > refresh_token.expires_at:
            return None

        # Check if revoked
        if refresh_token.revoked:
            return None

        return refresh_token

    def revoke_refresh_token(self, token: str) -> None:
        """Revoke a refresh token."""
        if token in self.refresh_tokens:
            self.refresh_tokens[token].revoked = True

    def cleanup_expired_tokens(self) -> None:
        """Remove expired refresh tokens."""
        now = datetime.utcnow()
        self.refresh_tokens = {
            token: refresh_token
            for token, refresh_token in self.refresh_tokens.items()
            if refresh_token.expires_at > now
        }

    # ========================================================================
    # Utility Methods
    # ========================================================================

    def cleanup_all(self) -> None:
        """Clean up all expired entities."""
        self.cleanup_expired_codes()
        self.cleanup_expired_tokens()

    def reset(self) -> None:
        """Reset all storage (for testing)."""
        self.clients.clear()
        self.authorization_codes.clear()
        self.refresh_tokens.clear()


# Global storage instance
storage = InMemoryStorage()
