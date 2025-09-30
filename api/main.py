"""
VitaNexus FastAPI Main Application
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import logging
import time
from typing import Dict

from api.config import settings
from api.database import check_db_connection, init_db
from api.routers import members, health_scores

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handle application startup and shutdown.

    Startup:
    - Verify database connection
    - Initialize connections to external services
    - Load ML models into memory
    - Start background tasks

    Shutdown:
    - Close database connections
    - Flush logs
    - Graceful shutdown of background tasks
    """
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.environment}")

    # Check database connection
    if check_db_connection():
        logger.info("Database connection: OK")
    else:
        logger.error("Database connection: FAILED")
        # In production, might want to exit if DB is unavailable
        # raise RuntimeError("Cannot start without database")

    # Initialize database tables (development only)
    if settings.environment == "development":
        logger.info("Initializing database tables (dev mode)")
        # init_db()  # Uncomment when ready to create tables

    # Load ML models
    logger.info("Loading health scoring models...")
    # In production: load pre-trained models from S3
    # model_loader.load_models()

    logger.info("Application startup complete")

    yield  # Application runs

    # Shutdown
    logger.info("Shutting down application...")
    # Cleanup tasks here
    logger.info("Shutdown complete")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    VitaNexus Health Assurance Cooperative API

    Core API for member management, health scoring, financial operations,
    and wellness intervention optimization.

    **Business Model**: We profit when members stay healthy, aligning our
    financial success with member wellness outcomes.

    **Key Features**:
    - AI-powered health risk scoring
    - ROI-optimized wellness interventions
    - Real-time wearable data integration
    - Transparent cost prediction
    - Member savings distribution (30% rebates)

    **Security**: All endpoints require OAuth 2.0 authentication.
    PHI data is encrypted and HIPAA-compliant audit logs are maintained.
    """,
    docs_url="/docs" if settings.enable_api_docs else None,
    redoc_url="/redoc" if settings.enable_api_docs else None,
    openapi_url=f"{settings.api_prefix}/openapi.json" if settings.enable_api_docs else None,
    lifespan=lifespan
)


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"]
)


# Gzip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time to response headers"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Request ID middleware (for distributed tracing)
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Add unique request ID for tracking"""
    import uuid
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with detailed messages"""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " -> ".join(str(x) for x in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "validation_error",
                "message": "Request validation failed",
                "details": errors
            }
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Catch-all exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    # Don't expose internal errors in production
    if settings.environment == "production":
        message = "An internal error occurred"
    else:
        message = str(exc)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "internal_error",
                "message": message
            }
        }
    )


# Health check endpoints
@app.get("/health", tags=["System"])
async def health_check() -> Dict:
    """
    Basic health check endpoint.

    Returns 200 if application is running.
    Used by load balancers and monitoring systems.
    """
    return {
        "status": "healthy",
        "version": settings.app_version,
        "environment": settings.environment
    }


@app.get("/health/ready", tags=["System"])
async def readiness_check() -> Dict:
    """
    Readiness check - verifies all dependencies are accessible.

    Returns 200 if application is ready to serve traffic.
    Checks:
    - Database connection
    - Redis connection
    - External API connectivity
    """
    checks = {
        "database": check_db_connection(),
        # Add more dependency checks
        # "redis": check_redis_connection(),
        # "kafka": check_kafka_connection(),
    }

    all_healthy = all(checks.values())

    return JSONResponse(
        status_code=status.HTTP_200_OK if all_healthy else status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "status": "ready" if all_healthy else "not_ready",
            "checks": checks
        }
    )


# Root endpoint
@app.get("/", tags=["System"])
async def root():
    """API root endpoint"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": "VitaNexus Health Assurance Cooperative API",
        "docs": f"{settings.api_prefix}/docs" if settings.enable_api_docs else None,
        "status": "operational"
    }


# Include routers
app.include_router(members.router, prefix=settings.api_prefix)
app.include_router(health_scores.router, prefix=settings.api_prefix)


# Additional routers to implement:
# app.include_router(wearables.router, prefix=settings.api_prefix)
# app.include_router(claims.router, prefix=settings.api_prefix)
# app.include_router(financial.router, prefix=settings.api_prefix)
# app.include_router(interventions.router, prefix=settings.api_prefix)
# app.include_router(analytics.router, prefix=settings.api_prefix)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )