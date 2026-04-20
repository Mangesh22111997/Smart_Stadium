"""
Centralised settings — loaded from environment variables.
On Cloud Run: set via --set-env-vars in gcloud run deploy.
Locally: set via .env file (never committed).
"""

import os
from dotenv import load_dotenv

load_dotenv()   # no-op when env vars already set (Cloud Run)

# Firebase
FIREBASE_API_KEY            = os.getenv("FIREBASE_API_KEY")
FIREBASE_AUTH_DOMAIN        = os.getenv("FIREBASE_AUTH_DOMAIN")
FIREBASE_DATABASE_URL       = os.getenv("FIREBASE_DATABASE_URL")
FIREBASE_PROJECT_ID         = os.getenv("FIREBASE_PROJECT_ID")
FIREBASE_STORAGE_BUCKET     = os.getenv("FIREBASE_STORAGE_BUCKET")
FIREBASE_MESSAGING_SENDER_ID = os.getenv("FIREBASE_MESSAGING_SENDER_ID")
FIREBASE_APP_ID             = os.getenv("FIREBASE_APP_ID")
FIREBASE_MEASUREMENT_ID     = os.getenv("FIREBASE_MEASUREMENT_ID")

# Google Maps
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")

# Security
SECRET_KEY = os.getenv("SECRET_KEY")

# Runtime
DEBUG   = os.getenv("DEBUG", "false").lower() == "true"
PORT    = int(os.getenv("PORT", 8080))    # Cloud Run default; local dev overrides to 8000

# CORS — Cloud Run frontend URL injected at deploy time
FRONTEND_URL = os.getenv("FRONTEND_URL", "")

# ── Startup validation ───────────────────────────────────────────────────────
# These must be set or the container will exit immediately with a clear message.
# This causes Cloud Run to show a useful error rather than a timeout.
_REQUIRED = ["FIREBASE_API_KEY", "FIREBASE_DATABASE_URL", "SECRET_KEY"]
for _var in _REQUIRED:
    if not os.getenv(_var):
        raise EnvironmentError(
            f"❌ Required environment variable '{_var}' is not set. "
            "Set it via --set-env-vars in gcloud run deploy "
            "or add it to your .env file for local development."
        )
