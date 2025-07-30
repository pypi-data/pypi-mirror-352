"""
Stytch B2B session token verification.

Handles verification of session tokens with the Stytch B2B API, including
caching, error handling, and session data extraction.
"""

import hashlib
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import stytch

from ..cache.redis_client import redis_client
from ..models.context import StytchContext
from ..utils.config import settings
from ..utils.exceptions import StytchAPIError, TokenVerificationError
from ..utils.logger import logger


class StytchVerifier:
    """
    Handles Stytch B2B session token verification with Redis caching.

    Provides a two-tier verification system:
    1. Check Redis cache for previously verified tokens
    2. Fall back to Stytch API for fresh verification
    """

    def __init__(self) -> None:
        self._client: Optional[stytch.B2BClient] = None

    def _get_client(self) -> stytch.B2BClient:
        """
        Get or create Stytch B2B client.

        Returns:
            Configured Stytch B2B client

        Raises:
            StytchAPIError: If client cannot be configured
        """
        if self._client is None:
            try:
                self._client = stytch.B2BClient(
                    project_id=settings.stytch_project_id,
                    secret=settings.stytch_secret,
                    environment=settings.stytch_environment,
                )
                logger.info("Stytch B2B client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Stytch client: {str(e)}")
                raise StytchAPIError(f"Stytch client initialization failed: {str(e)}")

        return self._client

    def _hash_token(self, token: str) -> str:
        """
        Create a hash of the token for cache key generation.

        Args:
            token: Session token to hash

        Returns:
            SHA256 hash of the token
        """
        return hashlib.sha256(token.encode()).hexdigest()

    async def verify_session_token(self, token: str) -> StytchContext:
        """
        Verify session token with caching support.

        Args:
            token: Stytch session token to verify

        Returns:
            StytchContext with session data

        Raises:
            TokenVerificationError: If token verification fails
            StytchAPIError: If Stytch API is unreachable
        """
        token_hash = self._hash_token(token)

        # Try cache first
        cached_result = await self._get_cached_verification(token_hash)
        if cached_result:
            return self._build_context_from_cache(cached_result)

        # Fall back to Stytch API
        session_data = await self._verify_with_stytch_api(token)

        # Cache the result
        await self._cache_verification_result(token_hash, session_data)

        return self._build_context_from_stytch_data(session_data)

    async def _get_cached_verification(
        self, token_hash: str
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached verification result.

        Args:
            token_hash: Hash of the token to look up

        Returns:
            Cached verification data if found and valid
        """
        try:
            cached_data = await redis_client.get_cached_verification(token_hash)
            if cached_data:
                # Check if cached session is still valid
                expires_at_str = cached_data.get("session_expires_at")
                if not expires_at_str or not isinstance(expires_at_str, str):
                    return None
                expires_at = datetime.fromisoformat(expires_at_str)
                if datetime.now(timezone.utc) < expires_at:
                    logger.debug("Using cached verification result")
                    return cached_data
                else:
                    logger.debug("Cached session expired, removing from cache")
                    await redis_client.delete_cached_verification(token_hash)

            return None

        except Exception as e:
            logger.warning(f"Cache lookup failed: {str(e)}")
            return None

    async def _verify_with_stytch_api(self, token: str) -> Dict[str, Any]:
        """
        Verify token directly with Stytch B2B API.

        Args:
            token: Session token to verify

        Returns:
            Raw session data from Stytch API

        Raises:
            TokenVerificationError: If token is invalid
            StytchAPIError: If API call fails
        """
        try:
            client = self._get_client()

            logger.debug("Verifying token with Stytch API")
            response = client.sessions.authenticate(session_token=token)

            if response.status_code != 200:
                logger.warning(
                    f"Stytch API returned error: {response.status_code}",
                    extra={
                        "response": (
                            response.json()
                            if hasattr(response, "json")
                            else str(response)
                        )
                    },
                )
                raise TokenVerificationError(
                    "Invalid or expired session token", token_hint=token[:8] + "..."
                )

            session_data = response.json()
            logger.info("Token verified successfully with Stytch API")
            return session_data

        except TokenVerificationError:
            # Re-raise token verification errors as-is
            raise

        except Exception as e:
            logger.error(f"Stytch API verification failed: {str(e)}", exc_info=True)
            raise StytchAPIError(
                f"Failed to verify token with Stytch: {str(e)}",
                api_response={"error": str(e)},
            )

    async def _cache_verification_result(
        self, token_hash: str, session_data: Dict[str, Any]
    ) -> None:
        """
        Cache verification result for future use.

        Args:
            token_hash: Hash of the verified token
            session_data: Session data from Stytch API
        """
        try:
            # Extract essential data for caching
            cache_data = {
                "member_id": session_data.get("member", {}).get("member_id"),
                "session_id": session_data.get("session", {}).get("session_id"),
                "organization_id": session_data.get("organization", {}).get(
                    "organization_id"
                ),
                "session_started_at": session_data.get("session", {}).get("started_at"),
                "session_expires_at": session_data.get("session", {}).get("expires_at"),
                "session_last_accessed_at": session_data.get("session", {}).get(
                    "last_accessed_at"
                ),
                "member_email": session_data.get("member", {}).get("email_address"),
                "member_name": session_data.get("member", {}).get("name"),
                "session_custom_claims": session_data.get("session", {}).get(
                    "custom_claims", {}
                ),
                "authentication_factors": session_data.get("session", {}).get(
                    "authentication_factors", []
                ),
                "raw_session_data": session_data,
                "cached_at": datetime.now(timezone.utc).isoformat(),
            }

            await redis_client.cache_verification_result(token_hash, cache_data)

        except Exception as e:
            logger.warning(f"Failed to cache verification result: {str(e)}")
            # Don't raise - caching failures should be non-fatal

    def _build_context_from_cache(self, cached_data: Dict[str, Any]) -> StytchContext:
        """
        Build StytchContext from cached verification data.

        Args:
            cached_data: Cached session data

        Returns:
            StytchContext instance
        """
        return StytchContext(
            member_id=cached_data["member_id"],
            session_id=cached_data["session_id"],
            organization_id=cached_data["organization_id"],
            session_started_at=datetime.fromisoformat(
                cached_data["session_started_at"]
            ),
            session_expires_at=datetime.fromisoformat(
                cached_data["session_expires_at"]
            ),
            session_last_accessed_at=datetime.fromisoformat(
                cached_data["session_last_accessed_at"]
            ),
            member_email=cached_data.get("member_email"),
            member_name=cached_data.get("member_name"),
            session_custom_claims=cached_data.get("session_custom_claims", {}),
            authentication_factors=cached_data.get("authentication_factors", []),
            raw_session_data=cached_data.get("raw_session_data", {}),
        )

    def _build_context_from_stytch_data(
        self, session_data: Dict[str, Any]
    ) -> StytchContext:
        """
        Build StytchContext from fresh Stytch API response.

        Args:
            session_data: Raw session data from Stytch API

        Returns:
            StytchContext instance
        """
        member = session_data.get("member", {})
        session = session_data.get("session", {})
        organization = session_data.get("organization", {})

        return StytchContext(
            member_id=member.get("member_id"),
            session_id=session.get("session_id"),
            organization_id=organization.get("organization_id"),
            session_started_at=datetime.fromisoformat(session.get("started_at")),
            session_expires_at=datetime.fromisoformat(session.get("expires_at")),
            session_last_accessed_at=datetime.fromisoformat(
                session.get("last_accessed_at")
            ),
            member_email=member.get("email_address"),
            member_name=member.get("name"),
            session_custom_claims=session.get("custom_claims", {}),
            authentication_factors=session.get("authentication_factors", []),
            raw_session_data=session_data,
        )


# Global verifier instance
stytch_verifier = StytchVerifier()
