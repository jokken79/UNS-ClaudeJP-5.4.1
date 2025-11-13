"""
Main FastAPI application for LolaAppJp

Entry point for the backend API
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time

from app.core.config import settings
from app.core.database import engine, Base

# Import routers (will be created)
# from app.api import auth, candidates, employees, factories, apartments, yukyu, timercards, payroll, requests


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan events

    On startup: Create database tables
    On shutdown: Clean up resources
    """
    # Startup
    print("🚀 Starting LolaAppJp backend...")
    print(f"📊 Database: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'local'}")

    # Create all database tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created/verified")

    yield

    # Shutdown
    print("👋 Shutting down LolaAppJp backend...")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="HR Management System for Japanese Staffing Agencies (人材派遣会社)",
    docs_url=f"{settings.API_V1_PREFIX}/docs",
    redoc_url=f"{settings.API_V1_PREFIX}/redoc",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    lifespan=lifespan,
)


# ============================================================================
# MIDDLEWARE
# ============================================================================

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add X-Process-Time header with request processing time"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# ============================================================================
# EXCEPTION HANDLERS
# ============================================================================

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Custom 404 handler"""
    return JSONResponse(
        status_code=404,
        content={"detail": "Resource not found", "path": str(request.url.path)},
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """Custom 500 handler"""
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "type": str(type(exc).__name__)},
    )


# ============================================================================
# ROUTES
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": f"{settings.API_V1_PREFIX}/docs",
    }


@app.get(f"{settings.API_V1_PREFIX}/health")
async def health_check():
    """Health check endpoint for Docker/Kubernetes"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


# ============================================================================
# API ROUTERS (to be added)
# ============================================================================

# app.include_router(auth.router, prefix=settings.API_V1_PREFIX, tags=["Authentication"])
# app.include_router(candidates.router, prefix=settings.API_V1_PREFIX, tags=["Candidates"])
# app.include_router(employees.router, prefix=settings.API_V1_PREFIX, tags=["Employees"])
# app.include_router(factories.router, prefix=settings.API_V1_PREFIX, tags=["Factories"])
# app.include_router(apartments.router, prefix=settings.API_V1_PREFIX, tags=["Apartments"])
# app.include_router(yukyu.router, prefix=settings.API_V1_PREFIX, tags=["Yukyu"])
# app.include_router(timercards.router, prefix=settings.API_V1_PREFIX, tags=["Timer Cards"])
# app.include_router(payroll.router, prefix=settings.API_V1_PREFIX, tags=["Payroll"])
# app.include_router(requests.router, prefix=settings.API_V1_PREFIX, tags=["Requests"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info",
    )
