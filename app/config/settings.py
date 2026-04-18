
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Firebase Configuration
FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY")
FIREBASE_AUTH_DOMAIN = os.getenv("FIREBASE_AUTH_DOMAIN")
FIREBASE_DATABASE_URL = os.getenv("FIREBASE_DATABASE_URL")
FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID")
FIREBASE_STORAGE_BUCKET = os.getenv("FIREBASE_STORAGE_BUCKET")
FIREBASE_MESSAGING_SENDER_ID = os.getenv("FIREBASE_MESSAGING_SENDER_ID")
FIREBASE_APP_ID = os.getenv("FIREBASE_APP_ID")
FIREBASE_MEASUREMENT_ID = os.getenv("FIREBASE_MEASUREMENT_ID")

# Google Maps
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

# Security
SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key-for-dev")

# App Settings
DEBUG = os.getenv("DEBUG", "True").lower() == "true"
PORT = int(os.getenv("PORT", 800))

# Validation
CRITICAL_VARS = ["FIREBASE_API_KEY", "FIREBASE_DATABASE_URL", "SECRET_KEY"]
for var in CRITICAL_VARS:
    if not os.getenv(var):
        print(f"⚠️ Warning: Environment variable {var} is not set.")
