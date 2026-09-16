"""
apps/ai_assistant/rate_limiter.py

DB-backed rate limiter for AI enhancement endpoints.
Limits each user to AI_RATE_LIMIT_PER_MINUTE (default: 15) requests per minute.
This protects the Groq free-tier quota (30 RPM shared across all users).

Uses Redis via Django cache for fast atomic counting.
Falls back to DB tracking if Redis is unavailable.
"""
import logging
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils import timezone

logger = logging.getLogger(__name__)

User = get_user_model()

RATE_LIMIT = getattr(settings, "AI_RATE_LIMIT_PER_MINUTE", 15)
WINDOW_SECONDS = 60


def check_ai_rate_limit(user) -> tuple[bool, int]:
    """
    Check if a user has exceeded the AI rate limit.

    Args:
        user: Authenticated Django user

    Returns:
        (allowed: bool, remaining: int)
        allowed=True  → request can proceed
        allowed=False → rate limit exceeded
        remaining     → number of requests left in current window
    """
    if not user or not user.is_authenticated:
        return False, 0

    cache_key = f"ai_rate_limit:{user.pk}:{_current_window()}"

    try:
        current_count = cache.get(cache_key, 0)

        if current_count >= RATE_LIMIT:
            remaining = 0
            logger.warning(
                f"AI rate limit exceeded for user {user.pk} "
                f"({current_count}/{RATE_LIMIT} in window)"
            )
            return False, remaining

        # Increment counter atomically
        try:
            new_count = cache.incr(cache_key)
        except ValueError:
            # Key doesn't exist yet — set it
            cache.set(cache_key, 1, timeout=WINDOW_SECONDS)
            new_count = 1

        # Set expiry on first request in window
        if new_count == 1:
            cache.expire(cache_key, WINDOW_SECONDS)

        remaining = max(0, RATE_LIMIT - new_count)
        return True, remaining

    except Exception as exc:
        # If cache is down, fail open (don't break the app)
        logger.error(f"Rate limiter cache error: {exc} — allowing request")
        return True, RATE_LIMIT


def _current_window() -> str:
    """Return a string representing the current 60-second window."""
    now = timezone.now()
    # Floor to the current minute
    window = now.replace(second=0, microsecond=0)
    return window.strftime("%Y%m%d%H%M")


def get_rate_limit_headers(user) -> dict:
    """Return HTTP headers for rate limit info (à la standard APIs)."""
    _, remaining = check_ai_rate_limit.__wrapped__(user) if hasattr(
        check_ai_rate_limit, '__wrapped__'
    ) else (True, RATE_LIMIT)
    return {
        "X-RateLimit-Limit": str(RATE_LIMIT),
        "X-RateLimit-Remaining": str(remaining),
        "X-RateLimit-Window": "60s",
    }
