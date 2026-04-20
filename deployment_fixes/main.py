"""
Smart Stadium System Backend — FastAPI entry point
Cloud Run compatible: reads PORT env var, CORS allows Cloud Run URLs
"""

import os
import time
import logging
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()   # no-op on Cloud Run (env vars set via --set-env-vars)

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.utils.limiter import limiter
from app.routes import (
    user_routes, ticket_routes, gate_routes, crowd_routes, reassignment_routes,
    food_routes, booth_allocation_routes, emergency_routes, notification_routes,
    staff_dashboard_routes, orchestration_routes, auth_routes,
    events_routes, bookings_routes,
)
from app.config.firebase_config import initialize_firebase, get_db_connection


# ============================================================================
# CLOUD LOGGING — wire before any logger.xxx calls
# ============================================================================

def setup_cloud_logging() -> None:
    """Route Python logging to Google Cloud Logging when running on GCP."""
    try:
        import google.cloud.logging
        client = google.cloud.logging.Client()
        client.setup_logging()
        print("✅ Google Cloud Logging active — logs visible in GCP Console")
    except Exception:
        logging.basicConfig(level=logging.INFO)
        print("ℹ️  Google Cloud Logging not configured — using local console logging")

setup_cloud_logging()
logger = logging.getLogger(__name__)


# ============================================================================
# FASTAPI APP
# ============================================================================

app = FastAPI(
    title="Smart Stadium System",
    description="Backend for Hack2Skill Smart Stadium — Firebase + ML crowd management",
    version="0.3.0",
)

# Attach rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# ============================================================================
# CORS — MUST include Cloud Run URLs and localhost for dev
# ============================================================================

def build_allowed_origins() -> list[str]:
    """
    Build CORS origin list from environment so Cloud Run URLs are included
    automatically without hardcoding them.
    """
    origins = [
        "http://localhost:8501",
        "http://localhost:8502",
        "http://localhost:8503",
        "http://localhost:8504",
        "http://localhost:8505",
        "http://localhost:8080",
    ]
    # Cloud Run frontend URL injected at deploy time
    frontend_url = os.getenv("FRONTEND_URL", "")
    if frontend_url:
        origins.append(frontend_url.rstrip("/"))

    # Allow any *.run.app origin for Cloud Run (covers all regions/revisions)
    # We add a wildcard-style check via a custom middleware instead — see below.
    return origins


app.add_middleware(
    CORSMiddleware,
    allow_origins=build_allowed_origins(),
    allow_origin_regex=r"https://.*\.run\.app",   # covers all Cloud Run services
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)


# ============================================================================
# AUDIT LOGGING MIDDLEWARE
# ============================================================================

@app.middleware("http")
async def audit_log_middleware(request: Request, call_next):
    """Log every request with method, path, status, and duration."""
    start = time.time()
    response = await call_next(request)
    duration_ms = round((time.time() - start) * 1000)
    logger.info(
        f"{request.method} {request.url.path} → {response.status_code} ({duration_ms}ms)"
    )
    return response


# ============================================================================
# ROUTERS
# ============================================================================

app.include_router(auth_routes.router)
app.include_router(user_routes.router)
app.include_router(ticket_routes.router)
app.include_router(gate_routes.router)
app.include_router(crowd_routes.router)
app.include_router(reassignment_routes.router)
app.include_router(food_routes.router)
app.include_router(booth_allocation_routes.router)
app.include_router(emergency_routes.router)
app.include_router(notification_routes.router)
app.include_router(staff_dashboard_routes.router)
app.include_router(orchestration_routes.router)
app.include_router(events_routes.router)
app.include_router(bookings_routes.router)


# ============================================================================
# SYSTEM ENDPOINTS
# ============================================================================

@app.get("/health", tags=["System"])
async def health_check():
    """Public health check — Cloud Run uses this to verify the container started."""
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "service": "Smart Stadium Backend",
        "version": "0.3.0",
    }


@app.get("/health/firebase", tags=["System"])
async def firebase_health_check():
    """Firebase Realtime Database connectivity check."""
    try:
        db = get_db_connection()
        db.child("system").child("status").get()
        return {"status": "ok", "database": "online"}
    except Exception as e:
        logger.error(f"Firebase health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={"status": "error", "database": "offline", "detail": str(e)},
        )


@app.get("/", tags=["System"])
async def root():
    """API root — lists available docs."""
    return {
        "message": "Smart Stadium System API",
        "docs": "/docs",
        "health": "/health",
    }


# ============================================================================
# GLOBAL EXCEPTION HANDLER
# ============================================================================

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all handler — always returns valid JSON, never exposes internals."""
    logger.error(f"Unhandled exception on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error", "detail": "An unexpected error occurred."},
    )


# ============================================================================
# STARTUP / SHUTDOWN
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """
    Cloud Run startup: Firebase init + ML model pre-warm.
    Must complete within the configured startup timeout (default 240s).
    """
    logger.info("🚀 Smart Stadium Backend starting...")

    # 1. Firebase
    try:
        initialize_firebase()
        db = get_db_connection()
        db.child("system").child("status").set({
            "status": "online",
            "startup_time": datetime.now().isoformat(),
            "version": "0.3.0",
        })
        logger.info("✅ Firebase Realtime Database — connected")
    except Exception as e:
        logger.warning(f"⚠️  Firebase init issue: {e} — continuing startup")

    # 2. ML inference pre-warm (non-fatal if models not present)
    try:
        from app.ml.inference_server import get_inference_server
        get_inference_server()
        logger.info("✅ ML inference server — pre-loaded")
    except Exception as e:
        logger.warning(f"⚠️  ML models not loaded: {e} — rule-based fallback active")

    logger.info("✅ Startup complete — accepting requests")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 Smart Stadium Backend shutting down")


# ============================================================================
# LOCAL DEV RUNNER — not used by Docker/Cloud Run
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
