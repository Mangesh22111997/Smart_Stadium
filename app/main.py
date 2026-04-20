
"""
Smart Stadium System Backend
Main entry point with FastAPI
"""
from fastapi import FastAPI, status
from dotenv import load_dotenv
import os

# Load environment variables early
load_dotenv()
from fastapi.responses import JSONResponse
from datetime import datetime
from app.routes import (
    user_routes, ticket_routes, gate_routes, crowd_routes, reassignment_routes,
    food_routes, booth_allocation_routes, emergency_routes, notification_routes,
    staff_dashboard_routes, orchestration_routes, auth_routes,
    events_routes, bookings_routes
)
from app.config.firebase_config import initialize_firebase, get_db_connection
import logging

from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from app.utils.limiter import limiter

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("smart_stadium")

def setup_cloud_logging():
    """
    Route Python logging to Google Cloud Logging if credentials are available.
    Falls back to local console logging gracefully.
    """
    try:
        import google.cloud.logging
        
        # Check if credentials file exists if path is provided
        cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if cred_path and not os.path.isabs(cred_path):
            # Convert relative path to absolute based on project root
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            abs_path = os.path.join(base_dir, cred_path)
            if os.path.exists(abs_path):
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = abs_path
                
        client = google.cloud.logging.Client()
        client.setup_logging()
        logger.info("✅ Google Cloud Logging active — logs visible in GCP Console")
        print("✅ Google Cloud Logging active — logs visible in GCP Console")
    except Exception as e:
        print(f"ℹ️  Google Cloud Logging not configured: {e} — using local console logging")

# Call before app creation
setup_cloud_logging()

# Initialize FastAPI app
app = FastAPI(
    title="Smart Stadium System",
    description="Backend for managing stadium crowd, gates, food, and emergencies with Firebase Realtime Database",
    version="0.2.0"
)

# Add Limiter to state
from slowapi import _rate_limit_exceeded_handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ============================================================================
# MIDDLEWARE
# ============================================================================

ALLOWED_ORIGINS = [
    "http://localhost:8501",   # Streamlit default
    "http://localhost:8502",
    "http://localhost:8503",
    "http://localhost:8504",
    "http://localhost:8505",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

# Audit Logging Middleware
import time
from fastapi import Request

@app.middleware("http")
async def audit_logging_middleware(request: Request, call_next):
    """
    Middleware to log all requests for audit purposes in GCP Console.
    """
    start_time = time.time()
    
    # Process request
    response = await call_next(request)
    
    # Calculate latency
    process_time = (time.time() - start_time) * 1000
    
    # Log audit entry
    logger.info(
        f"AUDIT | {request.method} {request.url.path} | "
        f"Status: {response.status_code} | Latency: {process_time:.2f}ms"
    )
    
    return response

# ============================================================================
# INCLUDE ROUTERS
# ============================================================================
# Authentication routes (must be first)
app.include_router(auth_routes.router)

# User and core routes
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

# New Phase 1 Routes (Events, Bookings, Gates Management)
app.include_router(events_routes.router)
app.include_router(bookings_routes.router)

# ============================================================================
# HEALTH CHECK ENDPOINT
# ============================================================================

@app.get("/health", tags=["System"])
async def health_check():
    """
    Health check endpoint to verify server is running
    Returns: Current timestamp and server status
    """
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "service": "Smart Stadium System Backend"
    }


@app.get("/health/firebase", tags=["System"])
async def firebase_health_check():
    """
    Firebase Realtime Database health check
    Returns: Database connection status
    """
    try:
        db = get_db_connection()
        
        # Test connection
        status_data = db.child("system").child("status").get()
        
        return {
            "status": "ok",
            "database": "online",
            "type": "Firebase Realtime Database",
            "current_status": status_data.val() if status_data.val() else "checking",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Firebase health check failed: {e}")
        return {
            "status": "error",
            "database": "offline",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


# ============================================================================
# ROOT ENDPOINT
# ============================================================================

@app.get("/", tags=["System"])
async def root():
    """
    Root endpoint - API information
    """
    return {
        "message": "Welcome to Smart Stadium System",
        "version": "0.2.0",
        "database": "Firebase Realtime Database",
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/health",
            "auth": "/docs#/Authentication",
            "firebase_health": "/health/firebase"
        }
    }


# ============================================================================
# STARTUP & SHUTDOWN EVENTS
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """
    Actions to perform on server startup
    Initialize Firebase Realtime Database and load services
    """
    try:
        print("🚀 Smart Stadium System Backend is starting...")
        print("📊 Project: Hack2Skill Google Challenge")
        print("\n🔥 Initializing Firebase Realtime Database...")
        
        # Initialize Firebase
        firebase_app = initialize_firebase()
        logger.info("✅ Firebase initialized successfully")
        
        # Verify database connection
        try:
            db = get_db_connection()
            
            # Test connection by writing test data
            db.child("system").child("status").set({
                "status": "online",
                "startup_time": datetime.now().isoformat(),
                "version": "0.2.0"
            })
            
            logger.info("✅ Firebase Realtime Database connection verified")
            print("✅ Firebase Realtime Database connection verified")
            print("✅ System Status: ONLINE\n")
            
        except Exception as e:
            logger.error(f"⚠️  Firebase connection test: {e}")
            print(f"⚠️  Firebase connection test: {e}\n")
        
        # Pre-load ML models so first prediction is instant
        try:
            from app.ml.inference_server import get_inference_server
            get_inference_server()
            logger.info("✅ ML inference server pre-loaded")
            print("✅ ML inference server pre-loaded")
        except Exception as e:
            logger.warning(f"⚠️  ML models not loaded: {e}. Rule-based fallback active.")
            print(f"⚠️  ML models not loaded: {e}")
            
        print("✅ All services initialized successfully\n")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        print(f"❌ Startup failed: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """
    Actions to perform on server shutdown
    """
    print("🛑 Smart Stadium System Backend is shutting down...")


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Global fallback exception handler — returns JSON, never a server crash."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": "An unexpected error occurred. Please try again."
        }
    )


# ============================================================================
# SERVER RUNNER
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    print("=" * 70)
    print("🏟️  SMART STADIUM SYSTEM - BACKEND")
    print("=" * 70)
    print("Starting server...")
    print("📍 URL: http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs")
    print("=" * 70)
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
