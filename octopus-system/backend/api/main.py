"""
Octopus Architecture - Main FastAPI Application
Master Directory System for Trust-Based Service Marketplaces
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import structlog
import time

from api.routes import providers, leads, bookings, trust, admin
from api.config import settings
from api.middleware import rate_limit_middleware, request_id_middleware
from api.exceptions import OctopusException

# Structured logging
logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    logger.info("Starting Octopus Architecture API", version=settings.VERSION)

    # Initialize Redis connection
    from api.utils.redis import redis_client
    await redis_client.ping()
    logger.info("Redis connected")

    # Initialize Supabase
    from api.utils.supabase import supabase_client
    logger.info("Supabase initialized")

    yield

    # Shutdown
    logger.info("Shutting down Octopus Architecture API")
    await redis_client.close()


# Initialize FastAPI app
app = FastAPI(
    title="Octopus Architecture API",
    description="Trust-based, agent-driven smart directory system",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted Host Middleware (Security)
if settings.ENVIRONMENT == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS,
    )

# GZip Compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Custom Middleware
app.middleware("http")(request_id_middleware)
app.middleware("http")(rate_limit_middleware)


# Exception Handlers
@app.exception_handler(OctopusException)
async def octopus_exception_handler(request: Request, exc: OctopusException):
    """Handle custom Octopus exceptions"""
    logger.error(
        "Octopus exception",
        error=exc.message,
        status_code=exc.status_code,
        path=request.url.path,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message, "detail": exc.detail},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    logger.exception(
        "Unhandled exception",
        path=request.url.path,
        method=request.method,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Internal server error", "detail": str(exc)},
    )


# Health Check
@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": time.time(),
    }


@app.get("/", tags=["System"])
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Octopus Architecture API",
        "version": settings.VERSION,
        "description": "Trust-based, agent-driven smart directory system",
        "docs": "/docs",
        "health": "/health",
        "city": settings.CITY_NAME,
        "tagline": "We deliver verified customers to verified businesses",
    }


# Schema.org Endpoint (Agent Discovery)
@app.get("/llms.txt", tags=["Agent"])
async def llms_protocol():
    """
    LLMS.txt protocol endpoint for AI agent discovery
    Allows agents to understand how to interact with this system
    """
    return {
        "protocol": "llms.txt",
        "version": "1.0",
        "service": "Octopus Architecture Directory",
        "capabilities": [
            "provider_search",
            "lead_capture",
            "booking_request",
            "trust_verification",
            "review_analysis",
        ],
        "endpoints": {
            "search_providers": "/api/v1/providers/search",
            "capture_lead": "/api/v1/leads/capture",
            "get_trust_score": "/api/v1/trust/{provider_id}",
            "request_booking": "/api/v1/bookings/request",
        },
        "authentication": "bearer_token",
        "rate_limits": {
            "requests_per_minute": 60,
            "requests_per_hour": 1000,
        },
        "documentation": "/docs",
    }


# Include API Routers
app.include_router(providers.router, prefix="/api/v1/providers", tags=["Providers"])
app.include_router(leads.router, prefix="/api/v1/leads", tags=["Leads"])
app.include_router(bookings.router, prefix="/api/v1/bookings", tags=["Bookings"])
app.include_router(trust.router, prefix="/api/v1/trust", tags=["Trust"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["Admin"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development",
        log_level="info",
    )
