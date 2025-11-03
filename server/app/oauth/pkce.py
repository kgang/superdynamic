"""
PKCE (Proof Key for Code Exchange) implementation per RFC 7636.

Provides utilities for generating and validating code challenges and verifiers.
"""

import hashlib
import base64
import secrets
from app.models import CodeChallengeMethod


def generate_code_verifier(length: int = 64) -> str:
    """
    Generate a cryptographically random code verifier.

    Args:
        length: Length of the verifier (43-128 characters, default 64)

    Returns:
        URL-safe base64-encoded random string
    """
    if length < 43 or length > 128:
        raise ValueError("Code verifier length must be between 43 and 128")

    # Generate random bytes
    random_bytes = secrets.token_bytes(length)

    # Base64 URL-safe encode and remove padding
    verifier = base64.urlsafe_b64encode(random_bytes).decode('utf-8')
    verifier = verifier.rstrip('=')

    # Ensure length constraint
    return verifier[:length]


def generate_code_challenge(
    code_verifier: str,
    method: CodeChallengeMethod = CodeChallengeMethod.S256
) -> str:
    """
    Generate a code challenge from a code verifier.

    Args:
        code_verifier: The code verifier string
        method: Challenge method (S256 or plain)

    Returns:
        The code challenge string
    """
    if method == CodeChallengeMethod.S256:
        # SHA-256 hash
        digest = hashlib.sha256(code_verifier.encode('utf-8')).digest()
        # Base64 URL-safe encode and remove padding
        challenge = base64.urlsafe_b64encode(digest).decode('utf-8')
        return challenge.rstrip('=')
    elif method == CodeChallengeMethod.PLAIN:
        # Plain method: challenge = verifier
        return code_verifier
    else:
        raise ValueError(f"Unsupported code challenge method: {method}")


def verify_code_challenge(
    code_verifier: str,
    code_challenge: str,
    method: CodeChallengeMethod = CodeChallengeMethod.S256
) -> bool:
    """
    Verify that a code verifier matches a code challenge.

    Args:
        code_verifier: The code verifier from token request
        code_challenge: The stored code challenge from authorization request
        method: The challenge method used

    Returns:
        True if the verifier matches the challenge, False otherwise
    """
    try:
        expected_challenge = generate_code_challenge(code_verifier, method)
        return expected_challenge == code_challenge
    except Exception:
        return False
