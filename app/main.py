"""
Smart Stadium System Backend
Main entry point with FastAPI
"""
from fastapi import FastAPI, status
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
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Limiter
limiter = Limiter(key_func=get_remote_address)

# Initialize FastAPI app
app = FastAPI(
    title="Smart Stadium System",
    description="Backend for managing stadium crowd, gates, food, and emergencies with Firebase Realtime Database",
    version="0.2.0"
)

# Add Limiter to state
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
    """
    Global exception handler
    """
    return {
        "error": "Internal Server Error",
        "detail": str(exc)
    }


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
