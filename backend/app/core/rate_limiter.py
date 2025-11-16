"""
Rate Limiting Service for AI Gateway

Provides per-user and per-IP rate limiting for AI API endpoints.

Rate Limits:
- Gemini: 100 calls per day
- OpenAI: 50 calls per day
- Claude API: 50 calls per day
- Local CLI: 200 calls per day (no cost)

Usage:
    from app.core.rate_limiter import limiter

    @router.post("/gemini")
    @limiter.limit("100/day")
    async def invoke_gemini(request, current_user):
        ...

Configuration:
    SLOWAPI_STORAGE_URL=memory:// (default: in-memory)
    SLOWAPI_STORAGE_URL=redis://localhost:6379 (for distributed)
"""

import logging
from typing import Optional, Dict
from datetime import datetime, timedelta

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import HTTPException, status, Request
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.core.config import settings

logger = logging.getLogger(__name__)

# Initialize rate limiter
# Uses in-memory storage by default (good for single instance)
# For distributed systems, use Redis
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200/hour"],  # Global fallback limit
    storage_uri=settings.SLOWAPI_STORAGE_URL if hasattr(settings, 'SLOWAPI_STORAGE_URL') else "memory://",
)


class RateLimitConfig:
    """Configuration for AI Gateway rate limits"""

    # Daily limits per provider (calls per day)
    GEMINI_LIMIT = "100/day"
    OPENAI_LIMIT = "50/day"
    CLAUDE_API_LIMIT = "50/day"
    LOCAL_CLI_LIMIT = "200/day"

    # Alternative per-minute limits for burst control
    GEMINI_BURST = "10/minute"
    OPENAI_BURST = "5/minute"
    CLAUDE_API_BURST = "5/minute"
    LOCAL_CLI_BURST = "20/minute"

    # Batch endpoint limits
    BATCH_LIMIT = "20/day"  # Max batch invocations per day


class UserRateLimitService:
    """
    Service to track and enforce user-based rate limits.

    Extends slowapi with per-user tracking and database persistence.
    Allows for custom limits per user and graceful limit increase.
    """

    def __init__(self, db: Session):
        """
        Initialize user rate limit service.

        Args:
            db: Database session for persistence
        """
        self.db = db
        self.limiter = limiter

    def get_user_limits(self, user_id: int) -> Dict[str, int]:
        """
        Get custom rate limits for a user.

        Args:
            user_id: User ID

        Returns:
            Dictionary with daily call limits per provider
        """
        # TODO: Implement custom limits from database
        # For now, return default limits
        return {
            "gemini": 100,
            "openai": 50,
            "claude_api": 50,
            "local_cli": 200,
        }

    def check_user_limit(self, user_id: int, provider: str) -> bool:
        """
        Check if user has exceeded daily limit for provider.

        Args:
            user_id: User ID
            provider: AI provider name (gemini, openai, claude_api, local_cli)

        Returns:
            True if within limit, False if exceeded

        Raises:
            HTTPException: If limit exceeded
        """
        # TODO: Implement database-backed limit checking
        # For now, rely on slowapi
        return True

    def record_usage(self, user_id: int, provider: str, tokens_used: int = 0):
        """
        Record API usage for tracking and analytics.

        Args:
            user_id: User ID
            provider: AI provider
            tokens_used: Number of tokens used (if applicable)
        """
        # TODO: Record to AIUsageLog table
        pass

    def get_usage_stats(self, user_id: int, days: int = 1) -> Dict[str, int]:
        """
        Get user usage statistics.

        Args:
            user_id: User ID
            days: Number of days to look back

        Returns:
            Dictionary with call counts per provider
        """
        # TODO: Query AIUsageLog table
        return {
            "gemini": 0,
            "openai": 0,
            "claude_api": 0,
            "local_cli": 0,
        }


def handle_rate_limit_error(request: Request, exc: RateLimitExceeded):
    """
    Custom error handler for rate limit exceeded.

    Args:
        request: FastAPI request
        exc: RateLimitExceeded exception

    Returns:
        HTTPException with detailed info
    """
    logger.warning(f"Rate limit exceeded for {request.client.host}: {exc.detail}")

    return HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail={
            "error": "Rate limit exceeded",
            "message": f"You have exceeded the rate limit. {exc.detail}",
            "retry_after": 3600,  # Suggest retry in 1 hour
            "documentation": "https://docs.uns-claudejp.com/api/rate-limiting"
        }
    )
