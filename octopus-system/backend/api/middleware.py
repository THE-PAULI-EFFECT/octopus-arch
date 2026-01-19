"""
Custom middleware for Octopus Architecture API
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time
import uuid
import structlog
from api.config import settings
from api.exceptions import RateLimitExceededException
from api.utils.redis import redis_client

logger = structlog.get_logger()


async def request_id_middleware(request: Request, call_next):
    """Add unique request ID to each request"""
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    # Add to logger context
    structlog.contextvars.bind_contextvars(request_id=request_id)

    # Start timer
    start_time = time.time()

    # Process request
    response = await call_next(request)

    # Calculate duration
    duration = time.time() - start_time

    # Add headers
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = str(duration)

    # Log request
    logger.info(
        "Request completed",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration=duration,
    )

    structlog.contextvars.clear_contextvars()

    return response


async def rate_limit_middleware(request: Request, call_next):
    """
    Redis-backed rate limiting middleware
    Implements sliding window rate limiting
    """

    # Skip rate limiting for health checks and docs
    if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"]:
        return await call_next(request)

    # Get client identifier (IP address or API key)
    client_id = request.client.host
    if "X-API-Key" in request.headers:
        client_id = f"api:{request.headers['X-API-Key']}"

    # Rate limit keys
    minute_key = f"rate_limit:minute:{client_id}"
    hour_key = f"rate_limit:hour:{client_id}"

    try:
        # Check minute limit
        minute_count = await redis_client.incr(minute_key)
        if minute_count == 1:
            await redis_client.expire(minute_key, 60)

        if minute_count > settings.RATE_LIMIT_PER_MINUTE:
            raise RateLimitExceededException()

        # Check hour limit
        hour_count = await redis_client.incr(hour_key)
        if hour_count == 1:
            await redis_client.expire(hour_key, 3600)

        if hour_count > settings.RATE_LIMIT_PER_HOUR:
            raise RateLimitExceededException()

        # Add rate limit headers to response
        response = await call_next(request)
        response.headers["X-RateLimit-Limit-Minute"] = str(
            settings.RATE_LIMIT_PER_MINUTE
        )
        response.headers["X-RateLimit-Remaining-Minute"] = str(
            settings.RATE_LIMIT_PER_MINUTE - minute_count
        )
        response.headers["X-RateLimit-Limit-Hour"] = str(settings.RATE_LIMIT_PER_HOUR)
        response.headers["X-RateLimit-Remaining-Hour"] = str(
            settings.RATE_LIMIT_PER_HOUR - hour_count
        )

        return response

    except RateLimitExceededException:
        raise
    except Exception as e:
        # If Redis fails, allow request but log error
        logger.error("Rate limiting failed", error=str(e))
        return await call_next(request)
