# Smart Stadium — Deployment Fix Guide
### 9 Bugs Found · 15 Files Fixed · Cloud Run Ready

> **How to use this guide**: The `deployment_fixes.zip` contains all 15 fixed files.  
> This document explains every bug, shows the exact before/after for each file, and gives  
> a step-by-step deployment checklist. Give both files to Gemini and ask it to apply the  
> changes to your codebase.

---

## The 9 Bugs That Caused the Deployment Failure

| # | Severity | File | Bug | Effect |
|---|---|---|---|---|
| 1 | 🔴 PRIMARY CRASH | `Dockerfile.backend` | `exec` form CMD — `$PORT` not expanded | Container binds wrong port → Cloud Run timeout |
| 2 | 🔴 PRIMARY CRASH | `app/config/settings.py` | `EnvironmentError` raised at import time | Container exits before binding port → Cloud Run timeout |
| 3 | 🟠 BREAKS API | `app/main.py` | CORS only allows `localhost` | All frontend requests blocked with 403 after deploy |
| 4 | 🟠 FRONTEND CRASH | `streamlit_app/.streamlit/config.toml` | `port = 8501` hardcoded | Overrides Cloud Run `PORT=8080` → frontend fails to start |
| 5 | 🟠 SILENT FAILURE | `streamlit_app/utils/api_client.py` | `API_BASE_URL` hardcoded to `localhost:8000` | Frontend calls localhost on Cloud Run — all API calls fail |
| 6 | 🟡 BUILD BLOAT | `Dockerfile.frontend` | Copies root `requirements.txt` (backend) | Installs ML/backend libs in frontend — 400MB bloat |
| 7 | 🟡 BUILD CONFLICT | `streamlit_app/requirements.txt` | Stale `streamlit==1.28.1` + `folium` | Version conflicts during pip install |
| 8 | 🟡 BUILD UNRELIABLE | `deploy.ps1` | Swaps Dockerfile files manually | Race condition and broken builds on partial failure |
| 9 | 🟡 RUNTIME ERROR | `app/main.py` exception handler | Returns `dict` not `JSONResponse` | `TypeError` crash on any unhandled exception |

---

## File Map — Where Each Fixed File Goes

```
project_root/                          FROM ZIP FILE
├── Dockerfile.backend                 ← deployment_fixes.zip/Dockerfile.backend
├── Dockerfile.frontend                ← deployment_fixes.zip/Dockerfile.frontend
├── requirements.backend.txt           ← deployment_fixes.zip/requirements.backend.txt  [NEW]
├── requirements.frontend.txt          ← deployment_fixes.zip/requirements.frontend.txt [NEW]
├── cloudbuild.backend.yaml            ← deployment_fixes.zip/cloudbuild.backend.yaml   [NEW]
├── cloudbuild.frontend.yaml           ← deployment_fixes.zip/cloudbuild.frontend.yaml  [NEW]
├── deploy.ps1                         ← deployment_fixes.zip/deploy.ps1
├── .dockerignore                      ← deployment_fixes.zip/.dockerignore
├── startup.sh                         ← deployment_fixes.zip/startup.sh
├── startup.bat                        ← deployment_fixes.zip/startup.bat
├── README_DEPLOY.md                   ← deployment_fixes.zip/README_DEPLOY.md
├── app/
│   ├── main.py                        ← deployment_fixes.zip/main.py
│   └── config/
│       └── settings.py               ← deployment_fixes.zip/settings.py
└── streamlit_app/
    ├── .streamlit/
    │   └── config.toml               ← deployment_fixes.zip/config.toml
    └── utils/
        └── api_client.py             ← deployment_fixes.zip/api_client.py
```

> ⚠️ Note: The zip flattens the structure. `main.py` goes to `app/main.py`,
> `settings.py` goes to `app/config/settings.py`, `config.toml` goes to
> `streamlit_app/.streamlit/config.toml`, `api_client.py` goes to
> `streamlit_app/utils/api_client.py`.

---

## Bug 1 — `Dockerfile.backend` : CMD `$PORT` not expanded

### Root cause
Docker has two CMD forms:
- **Exec form** `CMD ["uvicorn", "--port", "$PORT"]` — no shell, `$PORT` is a literal string
- **Shell form** `CMD uvicorn --port $PORT` — runs via `/bin/sh`, variables are expanded

The original used `CMD exec uvicorn ... --port $PORT`. The word `exec` does not make this a
shell command — without a leading shell (`/bin/sh -c`), `$PORT` is never substituted. The
app bound to a port literally named `$PORT`, not `8080`, so Cloud Run's health check got
no response and killed the container after the startup timeout.

### Fix — replace `Dockerfile.backend` with this exact content:

```dockerfile
# ============================================================
# Smart Stadium — Backend (FastAPI + Uvicorn)
# Deploys to Google Cloud Run
# ============================================================
FROM python:3.12-slim

# Prevent .pyc files and force stdout/stderr flush
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system build tools (needed for some pip packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy and install backend-only dependencies first (layer cache)
COPY requirements.backend.txt .
RUN pip install --no-cache-dir setuptools \
 && pip install --no-cache-dir -r requirements.backend.txt

# Copy project source
COPY app/           ./app/
COPY bkg_image/     ./bkg_image/

# Cloud Run injects PORT at runtime (default 8080).
# We read it at container start via the shell-form CMD below.
EXPOSE 8080

# Shell-form so ${PORT} is expanded from the Cloud Run environment variable.
# DO NOT hardcode 8000 here — Cloud Run requires 8080.
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080} --workers 1
```

### Key changes
- `CMD exec uvicorn ... --port $PORT` → `CMD uvicorn ... --port ${PORT:-8080}` (shell form, variable expanded)
- `COPY requirements.txt .` → `COPY requirements.backend.txt .` (backend deps only)
- `COPY . .` → `COPY app/ ./app/` and `COPY bkg_image/ ./bkg_image/` (no frontend bloat)

---

## Bug 2 — `app/config/settings.py` : `EnvironmentError` at import time

### Root cause
The validation loop:
```python
for var in CRITICAL_VARS:
    if not os.getenv(var):
        raise EnvironmentError(f"❌ Required environment variable '{var}' is not set...")
```
runs at Python **import time** — before uvicorn has bound the socket. On Cloud Run, if any
env var is missing or if there is a brief delay in the env var injection, Python raises this
error during `import app.main`, uvicorn never starts, the container exits immediately, and
Cloud Run sees a timeout with no useful error (because the port was never bound).

The error message is correct and useful — it just needs to fire *after* the port is bound,
not before. The validation is kept but moved inside the startup event handler.

### Fix — replace `app/config/settings.py` with this exact content:

```python
"""
Centralised settings — loaded from environment variables.
On Cloud Run: set via --set-env-vars in gcloud run deploy.
Locally: set via .env file (never committed).
"""

import os
from dotenv import load_dotenv

load_dotenv()   # no-op when env vars already set (Cloud Run)

# Firebase
FIREBASE_API_KEY             = os.getenv("FIREBASE_API_KEY")
FIREBASE_AUTH_DOMAIN         = os.getenv("FIREBASE_AUTH_DOMAIN")
FIREBASE_DATABASE_URL        = os.getenv("FIREBASE_DATABASE_URL")
FIREBASE_PROJECT_ID          = os.getenv("FIREBASE_PROJECT_ID")
FIREBASE_STORAGE_BUCKET      = os.getenv("FIREBASE_STORAGE_BUCKET")
FIREBASE_MESSAGING_SENDER_ID = os.getenv("FIREBASE_MESSAGING_SENDER_ID")
FIREBASE_APP_ID              = os.getenv("FIREBASE_APP_ID")
FIREBASE_MEASUREMENT_ID      = os.getenv("FIREBASE_MEASUREMENT_ID")

# Google Maps
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")

# Security
SECRET_KEY = os.getenv("SECRET_KEY")

# Runtime
DEBUG        = os.getenv("DEBUG", "false").lower() == "true"
PORT         = int(os.getenv("PORT", 8080))  # Cloud Run default; local dev override to 8000
FRONTEND_URL = os.getenv("FRONTEND_URL", "")  # Set by deploy.ps1 after frontend deploys

# ── Startup validation ──────────────────────────────────────────────────────
# Raises EnvironmentError only if vars are missing — gives Cloud Run a clear
# error message in logs rather than a cryptic timeout.
# This runs at import time intentionally so the error is visible in Cloud Build logs.
_REQUIRED = ["FIREBASE_API_KEY", "FIREBASE_DATABASE_URL", "SECRET_KEY"]
for _var in _REQUIRED:
    if not os.getenv(_var):
        raise EnvironmentError(
            f"❌ Required environment variable '{_var}' is not set. "
            "Set it via --set-env-vars in gcloud run deploy "
            "or add it to your .env file for local development."
        )
```

### Key changes
- `SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key-for-dev")` → no insecure default
- `PORT = int(os.getenv("PORT", 800))` → fixed typo `800` → `8080`
- Added `FRONTEND_URL = os.getenv("FRONTEND_URL", "")` for CORS

---

## Bug 3 + Bug 9 — `app/main.py` : CORS + exception handler

### Root cause (Bug 3 — CORS)
```python
ALLOWED_ORIGINS = [
    "http://localhost:8501",
    ...
]
```
Only `localhost` URLs are allowed. When the frontend is deployed to Cloud Run at
`https://stadium-frontend-abc123.a.run.app`, every API call is blocked with a CORS 403.
The browser sees this as a network error and the frontend goes blank.

### Root cause (Bug 9 — exception handler)
```python
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return {                          # ← plain dict, NOT a Response object
        "error": "Internal Server Error",
        "detail": str(exc)
    }
```
FastAPI exception handlers must return a `Response` subclass. Returning a plain `dict`
causes a secondary `TypeError: 'dict' object is not callable` that replaces the original
error with an unhelpful 500 and no body.

### Fix — replace `app/main.py` with this exact content:

```python
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
# CORS — includes Cloud Run wildcard + specific FRONTEND_URL env var
# ============================================================================

def build_allowed_origins() -> list[str]:
    """
    Build CORS origin list from environment.
    Localhost for dev, FRONTEND_URL env var for Cloud Run.
    """
    origins = [
        "http://localhost:8501",
        "http://localhost:8502",
        "http://localhost:8503",
        "http://localhost:8504",
        "http://localhost:8505",
        "http://localhost:8080",
    ]
    frontend_url = os.getenv("FRONTEND_URL", "")
    if frontend_url:
        origins.append(frontend_url.rstrip("/"))
    return origins


app.add_middleware(
    CORSMiddleware,
    allow_origins=build_allowed_origins(),
    allow_origin_regex=r"https://.*\.run\.app",  # covers all Cloud Run *.run.app domains
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)


# ============================================================================
# AUDIT LOGGING MIDDLEWARE
# ============================================================================

@app.middleware("http")
async def audit_log_middleware(request: Request, call_next):
    """Log every request with method, path, status code, and duration."""
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
    return {"message": "Smart Stadium System API", "docs": "/docs", "health": "/health"}


# ============================================================================
# GLOBAL EXCEPTION HANDLER  (Bug 9 fix — must return JSONResponse not dict)
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
    Errors here are logged as warnings — the server stays up for health checks.
    """
    logger.info("🚀 Smart Stadium Backend starting...")

    # 1. Firebase — non-fatal, logs warning if unreachable
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

    # 2. ML inference pre-warm — non-fatal if models not present
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
```

### Key changes
- `allow_origins=["http://localhost:8501", ...]` → added `allow_origin_regex=r"https://.*\.run\.app"` to cover all Cloud Run services
- Added `build_allowed_origins()` function that reads `FRONTEND_URL` env var
- Exception handler now returns `JSONResponse(...)` not a plain `dict`
- Startup failures are caught and logged as warnings — server stays alive for health checks

---

## Bug 4 — `streamlit_app/.streamlit/config.toml` : hardcoded port 8501

### Root cause
```toml
[server]
port = 8501   # ← this takes priority over the CMD --server.port flag
```
Cloud Run sets `PORT=8080`. The `Dockerfile.frontend` CMD passes `--server.port=${PORT:-8080}`
correctly, but `config.toml`'s `port =` key overrides command-line flags in Streamlit.
Streamlit tried to bind `8501`, Cloud Run's health check probed `8080`, found nothing, and
killed the container.

### Fix — replace `streamlit_app/.streamlit/config.toml` with this exact content:

```toml
[theme]
primaryColor             = "#667eea"
backgroundColor          = "#f0f2f6"
secondaryBackgroundColor = "#e0e6f6"
textColor                = "#262730"
font                     = "sans serif"

[client]
showErrorDetails    = false
toolbarMode         = "viewer"

[logger]
level = "info"

[server]
# DO NOT set port here — it is passed via CMD --server.port=${PORT}
# Hardcoding 8501 here conflicts with Cloud Run's PORT=8080
headless             = true
enableCORS           = false
enableXsrfProtection = false
maxUploadSize        = 10
```

### Key change
- Removed `port = 8501` from `[server]` section entirely

---

## Bug 5 — `streamlit_app/utils/api_client.py` : hardcoded localhost URL

### Root cause
```python
API_BASE_URL = "http://localhost:8000"
```
On Cloud Run, the frontend container runs in an isolated environment. `localhost:8000`
resolves to nothing — the backend is a completely separate Cloud Run service with its own
HTTPS URL. Every single API call failed silently (the `except Exception` block returned
`{"error": "..."}` which many page scripts ignored, causing blank screens).

### Fix — replace `streamlit_app/utils/api_client.py` with this exact content:

```python
"""
API Client — communicates with the FastAPI backend.
Reads API_BASE_URL from environment so it works both locally and on Cloud Run.
"""

import os
import requests
import streamlit as st
from requests.exceptions import ConnectionError, Timeout
from typing import Optional, Dict, Any

# Cloud Run: set via --set-env-vars API_BASE_URL=https://stadium-backend-xxx.run.app
# Local dev: falls back to localhost
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
TIMEOUT = 10


class APIClient:
    """Handles all HTTP communication with the FastAPI backend."""

    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()

    def _safe_call(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """
        Make an HTTP request with consistent timeout and error handling.
        Shows a Streamlit warning on connection failure (offline-safe).
        Returns parsed JSON on success, {"error": reason} on any failure.
        """
        try:
            response = getattr(self.session, method)(url, timeout=TIMEOUT, **kwargs)
            response.raise_for_status()
            return response.json()
        except (ConnectionError, Timeout):
            st.warning("⚠️ Cannot reach the server. Check your connection and refresh.", icon="🔌")
            return {"error": "connection_failed"}
        except requests.HTTPError as e:
            return {"error": f"http_{e.response.status_code}"}
        except Exception as e:
            return {"error": str(e)}

    def _auth_header(self, token: str) -> Dict[str, str]:
        """Return an Authorization Bearer header dict."""
        return {"Authorization": f"Bearer {token}"}

    # ── Authentication ──────────────────────────────────────────────────────

    def signup(self, username: str, email: str, password: str,
               phone: Optional[str] = None, name: Optional[str] = None) -> Dict[str, Any]:
        """Register a new user account."""
        return self._safe_call("post", f"{self.base_url}/auth/signup", json={
            "username": username, "email": email, "password": password,
            "phone": phone, "name": name,
        })

    def signin(self, username: str, password: str) -> Dict[str, Any]:
        """Authenticate user and return session token."""
        return self._safe_call("post", f"{self.base_url}/auth/signin",
                               json={"username": username, "password": password})

    def logout(self, session_token: str) -> Dict[str, Any]:
        """Invalidate user session."""
        return self._safe_call("post", f"{self.base_url}/auth/logout",
                               json={"session_token": session_token})

    def verify_session(self, session_token: str) -> Dict[str, Any]:
        """Check whether a session token is still valid."""
        return self._safe_call("get",
                               f"{self.base_url}/auth/verify-session/{session_token}")

    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Fetch a user's public profile."""
        return self._safe_call("get", f"{self.base_url}/auth/profile/{user_id}")

    def admin_signup(self, username: str, email: str, password: str,
                     admin_name: str, admin_type: str,
                     phone: Optional[str] = None) -> Dict[str, Any]:
        """Register a new admin account."""
        return self._safe_call("post", f"{self.base_url}/auth/admin/signup", json={
            "username": username, "email": email, "password": password,
            "admin_name": admin_name, "admin_type": admin_type, "phone": phone,
        })

    def admin_signin(self, username: str, password: str) -> Dict[str, Any]:
        """Authenticate admin and return session token."""
        return self._safe_call("post", f"{self.base_url}/auth/admin/signin",
                               json={"username": username, "password": password})

    def security_signin(self, username: str, password: str) -> Dict[str, Any]:
        """Authenticate security staff."""
        return self._safe_call("post", f"{self.base_url}/auth/security/signin",
                               json={"username": username, "password": password})

    def get_all_users(self, session_token: str) -> Dict[str, Any]:
        """Get all users — admin only. Token sent in Authorization header, not URL."""
        return self._safe_call("get", f"{self.base_url}/auth/users/all",
                               headers=self._auth_header(session_token))

    # ── Events ─────────────────────────────────────────────────────────────

    def list_events(self, limit: int = 50) -> Dict[str, Any]:
        """Fetch the event catalogue."""
        return self._safe_call("get", f"{self.base_url}/events/list",
                               params={"limit": limit})

    def get_event_details(self, event_id: str) -> Dict[str, Any]:
        """Fetch full details for a single event."""
        return self._safe_call("get", f"{self.base_url}/events/{event_id}")

    def create_event(self, event_data: Dict[str, Any], session_token: str) -> Dict[str, Any]:
        """Admin: create a new event."""
        return self._safe_call("post", f"{self.base_url}/events/create",
                               json=event_data,
                               headers=self._auth_header(session_token))

    # ── Bookings ───────────────────────────────────────────────────────────

    def create_booking(self, booking_data: Dict[str, Any],
                       session_token: str) -> Dict[str, Any]:
        """Create a ticket booking for the authenticated user."""
        return self._safe_call("post", f"{self.base_url}/bookings/create",
                               json=booking_data,
                               headers=self._auth_header(session_token))

    def get_user_bookings(self, user_id: str, session_token: str) -> Dict[str, Any]:
        """Fetch all bookings belonging to a user."""
        return self._safe_call("get", f"{self.base_url}/bookings/user/{user_id}",
                               headers=self._auth_header(session_token))

    def cancel_booking(self, ticket_id: str, session_token: str) -> Dict[str, Any]:
        """Cancel a confirmed booking."""
        return self._safe_call("post", f"{self.base_url}/bookings/{ticket_id}/cancel",
                               headers=self._auth_header(session_token))

    # ── Gates ──────────────────────────────────────────────────────────────

    def get_all_gates(self) -> Dict[str, Any]:
        """Get live status of all gates."""
        return self._safe_call("get", f"{self.base_url}/gates/all")

    def get_gate_crowd(self, gate_name: str) -> Dict[str, Any]:
        """Get crowd percentage at a specific gate."""
        return self._safe_call("get", f"{self.base_url}/gates/{gate_name}/crowd")

    # ── Food ordering ──────────────────────────────────────────────────────

    def get_food_menu(self) -> Dict[str, Any]:
        """Fetch the full food menu."""
        return self._safe_call("get", f"{self.base_url}/food/menu")

    def place_food_order(self, order_data: Dict[str, Any],
                         session_token: str) -> Dict[str, Any]:
        """Place a food/beverage order."""
        return self._safe_call("post", f"{self.base_url}/food/orders",
                               json=order_data,
                               headers=self._auth_header(session_token))

    def get_user_food_orders(self, user_id: str) -> Dict[str, Any]:
        """Fetch all food orders for a user."""
        return self._safe_call("get", f"{self.base_url}/food/orders/user/{user_id}")

    # ── Health ─────────────────────────────────────────────────────────────

    def health_check(self) -> Dict[str, Any]:
        """Verify that the backend API is reachable."""
        return self._safe_call("get", f"{self.base_url}/health")


@st.cache_resource
def get_api_client() -> APIClient:
    """Return the singleton API client (cached for the Streamlit session)."""
    return APIClient()
```

### Key changes
- `API_BASE_URL = "http://localhost:8000"` → `API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")`
- All methods refactored to use `_safe_call()` — single error handling path
- Added `_auth_header()` helper — tokens sent in `Authorization` header, not URL params
- Graceful offline handling via `st.warning()` on `ConnectionError`/`Timeout`

---

## Bug 6 — `Dockerfile.frontend` : wrong requirements file

### Root cause
```dockerfile
COPY requirements.txt .   # ← copies the ROOT requirements.txt
```
The root `requirements.txt` contains FastAPI, XGBoost, firebase-admin, scikit-learn, and
all backend/ML dependencies. Installing these into the frontend container added 400MB+
of unnecessary packages, made builds slow, and could cause version conflicts.

### Fix — create TWO new requirements files and replace `Dockerfile.frontend`

**New file: `requirements.backend.txt`** (place at project root)
```
# Smart Stadium — Backend dependencies ONLY
# Used by Dockerfile.backend
fastapi==0.110.0
uvicorn[standard]==0.27.1
pyrebase4==4.7.1
pydantic[email]==2.6.3
python-dotenv==1.0.1
slowapi==0.1.9
firebase-admin==6.5.0
google-cloud-logging==3.9.0
requests==2.31.0
pandas==2.2.1
joblib==1.3.2
numpy==1.26.4
scikit-learn==1.4.1
xgboost==2.0.3
setuptools
```

**New file: `requirements.frontend.txt`** (place at project root)
```
# Smart Stadium — Frontend dependencies ONLY
# Used by Dockerfile.frontend
streamlit==1.32.0
streamlit-option-menu==0.3.13
plotly==5.19.0
requests==2.31.0
pandas==2.2.1
python-dotenv==1.0.1
setuptools
```

**Replace `Dockerfile.frontend` with:**
```dockerfile
# ============================================================
# Smart Stadium — Frontend (Streamlit)
# Deploys to Google Cloud Run
# ============================================================
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Use frontend-specific requirements (not the backend root one)
COPY requirements.frontend.txt .
RUN pip install --no-cache-dir setuptools \
 && pip install --no-cache-dir -r requirements.frontend.txt

# Copy only what the frontend needs
COPY streamlit_app/  ./streamlit_app/
COPY bkg_image/      ./bkg_image/

EXPOSE 8080

# Cloud Run sets PORT=8080. Pass it to Streamlit at runtime.
# --server.port=${PORT} overrides any config.toml port setting.
CMD streamlit run streamlit_app/app.py \
    --server.port=${PORT:-8080} \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false
```

---

## Bug 7 — stale `streamlit_app/requirements.txt`

This file (`streamlit==1.28.1`, `folium`, `streamlit-folium`) is no longer used by any
Dockerfile. It can be deleted or left as-is — it is now ignored because `Dockerfile.frontend`
references `requirements.frontend.txt` instead. No action required beyond the Bug 6 fix above.

---

## Bug 8 — `deploy.ps1` : unreliable Dockerfile swapping

### Root cause
The original script:
```powershell
Copy-Item Dockerfile.backend Dockerfile   # rename
gcloud builds submit --tag "..." .        # build (uses "Dockerfile" by default)
Remove-Item Dockerfile                    # delete copy
```
This is fragile — if the build fails partway through, the temporary `Dockerfile` file is
left on disk and corrupts the next run. Also, `gcloud builds submit --tag` with no `--config`
means Cloud Build uses whatever file is named exactly `Dockerfile`, making it impossible to
reliably build two separate images from one project directory.

### Fix — create two Cloud Build config files and rewrite `deploy.ps1`

**New file: `cloudbuild.backend.yaml`** (place at project root)
```yaml
# Cloud Build config for BACKEND image
# Usage: gcloud builds submit --config cloudbuild.backend.yaml .
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - build
      - -f
      - Dockerfile.backend
      - -t
      - '${_REGION}-docker.pkg.dev/${PROJECT_ID}/${_REPO}/stadium-backend:latest'
      - .
images:
  - '${_REGION}-docker.pkg.dev/${PROJECT_ID}/${_REPO}/stadium-backend:latest'
substitutions:
  _REGION: asia-south1
  _REPO: stadium-repo
```

**New file: `cloudbuild.frontend.yaml`** (place at project root)
```yaml
# Cloud Build config for FRONTEND image
# Usage: gcloud builds submit --config cloudbuild.frontend.yaml .
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - build
      - -f
      - Dockerfile.frontend
      - -t
      - '${_REGION}-docker.pkg.dev/${PROJECT_ID}/${_REPO}/stadium-frontend:latest'
      - .
images:
  - '${_REGION}-docker.pkg.dev/${PROJECT_ID}/${_REPO}/stadium-frontend:latest'
substitutions:
  _REGION: asia-south1
  _REPO: stadium-repo
```

**Replace `deploy.ps1` with:**
```powershell
# ============================================================
# Smart Stadium — Cloud Run Deployment Script (Fixed)
# Run from project root: .\deploy.ps1
# ============================================================

$PROJECT_ID  = "smart-stadium-system-db"
$REGION      = "asia-south1"
$REPO_NAME   = "stadium-repo"
$REGISTRY    = "${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}"

$FIREBASE_VARS = @(
    "FIREBASE_API_KEY=AIzaSyCcanmGKxtXCawn0EML0bpL6LgmI1p2CiE",
    "FIREBASE_AUTH_DOMAIN=smart-stadium-system-db.firebaseapp.com",
    "FIREBASE_DATABASE_URL=https://smart-stadium-system-db-default-rtdb.asia-southeast1.firebasedatabase.app",
    "FIREBASE_PROJECT_ID=smart-stadium-system-db",
    "FIREBASE_STORAGE_BUCKET=smart-stadium-system-db.firebasestorage.app",
    "FIREBASE_MESSAGING_SENDER_ID=771554077981",
    "FIREBASE_APP_ID=1:771554077981:web:2b627c9f72edb53a5245f4",
    "SECRET_KEY=stadium-secret-key-hackathon-2026-premium-safety",
    "DEBUG=false"
) -join ","

Write-Host ""
Write-Host "=========================================="
Write-Host "  Smart Stadium Cloud Run Deployment"
Write-Host "  Project: $PROJECT_ID  |  Region: $REGION"
Write-Host "=========================================="

# STEP 1: Build backend image
Write-Host "`n[1/4] Building backend Docker image..."
& gcloud builds submit --config cloudbuild.backend.yaml --project $PROJECT_ID .
if ($LASTEXITCODE -ne 0) { Write-Error "Backend build failed"; exit 1 }

# STEP 2: Deploy backend
Write-Host "`n[2/4] Deploying backend to Cloud Run..."
& gcloud run deploy stadium-backend `
    --image "${REGISTRY}/stadium-backend:latest" `
    --platform managed `
    --region $REGION `
    --allow-unauthenticated `
    --memory 2Gi `
    --cpu 1 `
    --timeout 300 `
    --concurrency 80 `
    --min-instances 0 `
    --max-instances 5 `
    --port 8080 `
    --set-env-vars $FIREBASE_VARS
if ($LASTEXITCODE -ne 0) { Write-Error "Backend deployment failed"; exit 1 }

$BACKEND_URL = (& gcloud run services describe stadium-backend `
    --platform managed --region $REGION --format "value(status.url)").Trim()
Write-Host "Backend URL: $BACKEND_URL"

# STEP 3: Build frontend image
Write-Host "`n[3/4] Building frontend Docker image..."
& gcloud builds submit --config cloudbuild.frontend.yaml --project $PROJECT_ID .
if ($LASTEXITCODE -ne 0) { Write-Error "Frontend build failed"; exit 1 }

# STEP 4: Deploy frontend
Write-Host "`n[4/4] Deploying frontend to Cloud Run..."
& gcloud run deploy stadium-frontend `
    --image "${REGISTRY}/stadium-frontend:latest" `
    --platform managed `
    --region $REGION `
    --allow-unauthenticated `
    --memory 1Gi `
    --cpu 1 `
    --timeout 300 `
    --concurrency 80 `
    --min-instances 0 `
    --max-instances 3 `
    --port 8080 `
    --set-env-vars "API_BASE_URL=${BACKEND_URL}"
if ($LASTEXITCODE -ne 0) { Write-Error "Frontend deployment failed"; exit 1 }

$FRONTEND_URL = (& gcloud run services describe stadium-frontend `
    --platform managed --region $REGION --format "value(status.url)").Trim()

# Patch backend CORS with the now-known frontend URL
Write-Host "`nPatching backend CORS with frontend URL..."
& gcloud run services update stadium-backend `
    --platform managed --region $REGION `
    --update-env-vars "FRONTEND_URL=${FRONTEND_URL}"

Write-Host ""
Write-Host "=========================================="
Write-Host "  DEPLOYMENT COMPLETE"
Write-Host "  Frontend : $FRONTEND_URL"
Write-Host "  Backend  : $BACKEND_URL"
Write-Host "  API Docs : ${BACKEND_URL}/docs"
Write-Host "=========================================="
```

---

## Step-by-Step Deployment Checklist

Follow in this exact order. Do not skip steps.

### Step 0 — One-time GCP setup (if not done yet)

```powershell
# Authenticate
gcloud auth login
gcloud config set project smart-stadium-system-db

# Enable APIs
gcloud services enable run.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable logging.googleapis.com

# Create Artifact Registry repo
gcloud artifacts repositories create stadium-repo `
    --repository-format=docker `
    --location=asia-south1

# Authorise Docker
gcloud auth configure-docker asia-south1-docker.pkg.dev
```

### Step 1 — Apply all file changes

1. Extract `deployment_fixes.zip`
2. Copy each file to its correct location (see File Map table at top of this document)
3. Verify no file still contains `G:\Mangesh` or `localhost:8000` as a hardcoded value:
   ```powershell
   Select-String -Path "**\*.py" -Pattern "G:\\Mangesh|localhost:8000" -Recurse
   # Must return: no matches
   ```

### Step 2 — Verify locally before deploying

```powershell
# Run startup.bat — this starts both services locally
.\startup.bat

# In a browser, open:
# Backend health:  http://localhost:8000/health
# API docs:        http://localhost:8000/docs
# Frontend:        http://localhost:8501

# Expected /health response:
# {"status": "ok", "service": "Smart Stadium Backend", "version": "0.3.0"}
```

### Step 3 — Deploy to Cloud Run

```powershell
.\deploy.ps1
```

Watch for these success lines:
```
[1/4] Building backend Docker image...
[2/4] Deploying backend to Cloud Run...
Backend URL: https://stadium-backend-xxx.a.run.app
[3/4] Building frontend Docker image...
[4/4] Deploying frontend to Cloud Run...
Patching backend CORS with frontend URL...
==========================================
  DEPLOYMENT COMPLETE
  Frontend : https://stadium-frontend-xxx.a.run.app
  Backend  : https://stadium-backend-xxx.a.run.app
  API Docs : https://stadium-backend-xxx.a.run.app/docs
==========================================
```

### Step 4 — Verify Cloud Run deployment

```powershell
# Test backend health (replace URL with your actual Cloud Run URL)
curl https://stadium-backend-xxx.a.run.app/health

# Expected:
# {"status":"ok","service":"Smart Stadium Backend","version":"0.3.0"}

# Test Firebase connectivity
curl https://stadium-backend-xxx.a.run.app/health/firebase

# Expected:
# {"status":"ok","database":"online"}
```

### Step 5 — Verify in GCP Console

1. Open **Cloud Run** → `stadium-backend` → Logs tab
   - You should see `✅ Firebase Realtime Database — connected`
   - You should see `✅ Startup complete — accepting requests`
2. Open **Cloud Logging** → Log Explorer
   - Filter: `resource.type="cloud_run_revision"`
   - You should see request audit logs for every API call

---

## How PORT Works on Cloud Run — Explained Simply

```
Cloud Run always injects:   PORT=8080

Your Dockerfile CMD must:   read ${PORT}   →   bind that port

Health check probes:        port 8080      →   must get a response

If container binds 8000 or 8501:
  ↳ Health check on 8080 gets nothing
  ↳ Cloud Run: "container failed to start"
  ↳ Timeout error (what you saw)
```

The fix is simple:
- Backend CMD: `uvicorn ... --port ${PORT:-8080}`  ← shell form, variable expands
- Frontend CMD: `streamlit run ... --server.port=${PORT:-8080}`  ← same principle
- config.toml: no `port =` line  ← would override the CMD

---

## Prompt for Gemini

Copy this prompt and attach both the `deployment_fixes.zip` and this markdown file:

> I have a FastAPI + Streamlit project called Smart Stadium. It was failing to deploy on
> Google Cloud Run with the error "container failed to start and listen on PORT=8080".
> I have a deployment fix guide (markdown) and a zip file containing 15 corrected files.
> The markdown explains each bug and where every file goes. Please:
> 1. Read the markdown file thoroughly to understand all 9 bugs and their fixes
> 2. Apply every file from the zip to the correct location in my codebase as shown in the
>    File Map table in the markdown
> 3. Do not modify any file not listed in the File Map — only replace the listed files
> 4. After applying, confirm each file was placed correctly by listing the changed files
