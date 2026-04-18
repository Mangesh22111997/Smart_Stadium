# Smart Stadium System — Hackathon Standards Compliance Guide

> **Based on**: `STADIUM_SYSTEM_GUIDE.md` (GCP/Firebase track)  
> **Judging criteria**: Code Quality · Security · Efficiency · Testing · Accessibility · Google Services  
> **Purpose**: Exact actions to bring the codebase to hackathon-winning standard across all 6 criteria

---

## Quick Compliance Scorecard

| Criterion | Current State | Gap | Priority |
|---|---|---|---|
| Code Quality | Functional but inconsistent structure | Missing docstrings, type hints, linting | HIGH |
| Security | Firebase Auth present, credentials at risk | Secrets in config files, no input sanitisation | CRITICAL |
| Efficiency | Works for demo scale | No caching, blocking API calls, heavy assets | HIGH |
| Testing | No test suite mentioned | Zero automated tests | HIGH |
| Accessibility | Single language, no contrast/ARIA work | No keyboard nav, hardcoded English only | MEDIUM |
| Google Services | Firebase + Maps integrated | Underutilised — Vertex AI, Cloud Run, Logging missing | MEDIUM |

---

## Criterion 1: Code Quality

### What judges look for
Clean module boundaries, consistent naming, self-documenting functions, no dead code, logical file organisation.

### Issues in the current codebase

**Issue 1.1 — Numeric page prefixes are not semantic**

Page files named `3_Home.py`, `4_Events.py`, `7_Food.py`, `16_Event_Booking.py` are Streamlit routing convention but the large gaps in numbering (7 → 16) suggest deleted pages left behind. Rename to sequential, descriptive names.

```
Before:                         After:
3_Home.py              →        01_home.py
4_Events.py            →        02_events.py
5_Bookings.py          →        03_bookings.py
6_Maps.py              →        04_maps.py
7_Food.py              →        05_food.py
16_Event_Booking.py    →        06_event_booking.py
```

**Issue 1.2 — No type hints or docstrings**

Every public function must have a type signature and a one-line docstring. This is the single most visible quality signal to a judge reading code.

```python
# Before (what judges see as amateur)
def get_user_bookings(user_id):
    result = firebase_client.get(f"bookings/{user_id}")
    return result

# After (what judges see as professional)
def get_user_bookings(user_id: str) -> list[dict]:
    """Retrieve all confirmed bookings for a given user from Firebase RTDB."""
    result = firebase_client.get(f"bookings/{user_id}")
    return result or []
```

Apply this pattern to every function in `/services`, `/routes`, and `/utils`.

**Issue 1.3 — `firebase_config.py` is doing too much**

A config file should only hold constants and initialisation. Business logic (CRUD operations) should not live inside it. Split it:

```
/config/
    firebase_config.py      ← credentials + app init only
    settings.py             ← environment-level constants (port, debug flag, API keys)

/services/
    firebase_client.py      ← all read/write/delete wrappers  [MOVED FROM CONFIG]
```

**Issue 1.4 — `ui_helper.py` is overloaded**

One file handling premium styling, database fetching, and animations violates the single-responsibility principle. Split it:

```
/utils/
    ui_helper.py            ← CSS injection and layout helpers only
    asset_loader.py         ← Firebase RTDB asset fetching (Base64 images, GIFs)
    animation_helper.py     ← Interwind animation logic
```

**Issue 1.5 — Add a `.flake8` config and enforce it**

Create at the project root:

```ini
# .flake8
[flake8]
max-line-length = 100
exclude = .venv, __pycache__, data/generated
per-file-ignores =
    __init__.py: F401
```

Run before submission:

```bash
pip install flake8
flake8 app/ streamlit_app/
# Must return zero errors
```

**Issue 1.6 — Add a `README.md` to the project root**

Judges often look at the repo landing page first. It must contain:

```markdown
## Setup in 3 commands
git clone <repo>
pip install -r requirements.txt
python seed_test_users.py && uvicorn app.main:app & streamlit run streamlit_app/app.py

## Test credentials
Admin  — email: admin@stadium.com  password: Admin@123
User   — email: test@stadium.com   password: Test@123
```

---

## Criterion 2: Security

### What judges look for
No hardcoded secrets, input validation, protection against common vulnerabilities (injection, broken auth, data exposure).

### Issues in the current codebase

**Issue 2.1 — CRITICAL: Firebase credentials must not be in source code**

`firebase_config.py` almost certainly contains a service account JSON or API key inline. This is an automatic disqualification risk if the repo is public.

Step 1 — Move all secrets to a `.env` file:

```bash
# .env  (this file is NEVER committed)
FIREBASE_API_KEY=AIzaSy...
FIREBASE_AUTH_DOMAIN=stadium-app.firebaseapp.com
FIREBASE_DATABASE_URL=https://stadium-app-default-rtdb.firebaseio.com
FIREBASE_STORAGE_BUCKET=stadium-app.appspot.com
GOOGLE_MAPS_API_KEY=AIzaSy...
SECRET_KEY=your-jwt-secret-minimum-32-chars
```

Step 2 — Load via `python-dotenv`:

```python
# app/config/settings.py
from dotenv import load_dotenv
import os

load_dotenv()

FIREBASE_API_KEY       = os.getenv("FIREBASE_API_KEY")
FIREBASE_DATABASE_URL  = os.getenv("FIREBASE_DATABASE_URL")
GOOGLE_MAPS_API_KEY    = os.getenv("GOOGLE_MAPS_API_KEY")
SECRET_KEY             = os.getenv("SECRET_KEY")

# Fail loudly at startup if any critical variable is missing
for var_name in ["FIREBASE_API_KEY", "FIREBASE_DATABASE_URL", "SECRET_KEY"]:
    if not os.getenv(var_name):
        raise EnvironmentError(f"Required environment variable '{var_name}' is not set.")
```

Step 3 — Add `.env` to `.gitignore` and add `.env.example` with dummy values:

```bash
# .env.example  (this IS committed — shows structure without real values)
FIREBASE_API_KEY=your-firebase-api-key-here
FIREBASE_DATABASE_URL=https://your-project-default-rtdb.firebaseio.com
GOOGLE_MAPS_API_KEY=your-google-maps-api-key-here
SECRET_KEY=generate-a-random-32-char-string-here
```

**Issue 2.2 — Input validation is missing on booking and food routes**

Every field that accepts user text must be validated and sanitised before it touches Firebase.

```python
# app/models/ticket.py — add validators
from pydantic import BaseModel, field_validator, EmailStr
import re

class BookingRequest(BaseModel):
    user_id: str
    event_id: str
    seat_zone: str
    quantity: int
    commute_mode: str
    group_size: int

    @field_validator("seat_zone")
    @classmethod
    def validate_seat_zone(cls, v: str) -> str:
        allowed = {"A", "B", "C", "D"}
        if v.upper() not in allowed:
            raise ValueError(f"seat_zone must be one of {allowed}")
        return v.upper()

    @field_validator("quantity")
    @classmethod
    def validate_quantity(cls, v: int) -> int:
        if not 1 <= v <= 10:
            raise ValueError("quantity must be between 1 and 10")
        return v

    @field_validator("commute_mode")
    @classmethod
    def validate_commute_mode(cls, v: str) -> str:
        allowed = {"metro", "private_car", "cab", "bus", "walk"}
        if v.lower() not in allowed:
            raise ValueError(f"commute_mode must be one of {allowed}")
        return v.lower()

    @field_validator("group_size")
    @classmethod
    def validate_group_size(cls, v: int) -> int:
        if not 1 <= v <= 20:
            raise ValueError("group_size must be between 1 and 20")
        return v
```

**Issue 2.3 — Firebase Authentication token must be verified server-side**

Firebase Auth on the client generates an ID token. That token must be verified on every protected backend request — not just trusted because the frontend sent it.

```python
# app/utils/auth_middleware.py
import firebase_admin.auth as firebase_auth
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

def verify_firebase_token(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> dict:
    """Verify Firebase ID token and return decoded claims. Raise 401 if invalid."""
    token = credentials.credentials
    try:
        decoded = firebase_auth.verify_id_token(token)
        return decoded
    except firebase_auth.ExpiredIdTokenError:
        raise HTTPException(status_code=401, detail="Token has expired. Please log in again.")
    except firebase_auth.InvalidIdTokenError:
        raise HTTPException(status_code=401, detail="Invalid authentication token.")
    except Exception:
        raise HTTPException(status_code=401, detail="Authentication failed.")
```

Apply to every protected route:

```python
# app/routes/bookings_routes.py
from app.utils.auth_middleware import verify_firebase_token

@router.post("/bookings/create")
async def create_booking(
    request: BookingRequest,
    current_user: dict = Depends(verify_firebase_token)   # ← add this
):
    # current_user["uid"] is now verified from Firebase
    if current_user["uid"] != request.user_id:
        raise HTTPException(status_code=403, detail="You can only book tickets for your own account.")
    ...
```

**Issue 2.4 — CORS must be restricted**

`main.py` almost certainly has `allow_origins=["*"]`. For a hackathon demo this is a red flag.

```python
# app/main.py
from fastapi.middleware.cors import CORSMiddleware

ALLOWED_ORIGINS = [
    "http://localhost:8501",   # Streamlit dev
    "http://localhost:8503",   # Alternate Streamlit port
    # Add your GCP Cloud Run URL here when deployed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT"],   # never ["*"]
    allow_headers=["Authorization", "Content-Type"],
)
```

**Issue 2.5 — Add rate limiting to auth endpoints**

Prevents brute-force login attempts. One decorator, high impact.

```bash
pip install slowapi
```

```python
# app/main.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# app/routes/auth_routes.py
@router.post("/auth/login")
@limiter.limit("5/minute")   # max 5 login attempts per minute per IP
async def login(request: Request, credentials: LoginRequest):
    ...
```

---

## Criterion 3: Efficiency

### What judges look for
No unnecessary computation, smart caching, async-first design, assets loaded efficiently.

### Issues in the current codebase

**Issue 3.1 — Firebase RTDB calls are made on every page render**

Streamlit reruns the entire script on every user interaction. Without caching, every button click fires a Firebase read. Use `st.cache_data` for data that does not change per-user and per-session.

```python
# streamlit_app/utils/asset_loader.py

import streamlit as st

@st.cache_data(ttl=3600)   # cache for 1 hour — background images don't change
def load_background_image() -> str:
    """Fetch Base64 background image from Firebase RTDB. Cached for 1 hour."""
    return firebase_client.get("assets/background_image")

@st.cache_data(ttl=300)    # cache for 5 minutes — event list changes occasionally
def load_event_catalog() -> list[dict]:
    """Fetch all available events from Firebase RTDB."""
    return firebase_client.get("events") or []

# Per-user data: do NOT cache — must be fresh
def load_user_bookings(user_id: str) -> list[dict]:
    """Fetch user's bookings. Not cached — must reflect latest state."""
    return firebase_client.get(f"bookings/{user_id}") or []
```

**Issue 3.2 — All FastAPI routes must be async**

Any route that calls Firebase or any I/O must be `async def`, not `def`. A synchronous route blocks the entire event loop.

```python
# Before (blocks the event loop)
@router.get("/events")
def get_events():
    return firebase_client.get("events")

# After (non-blocking)
@router.get("/events")
async def get_events():
    return await firebase_client.async_get("events")
```

**Issue 3.3 — ML model loading must be lazy and cached**

If the ML inference server loads all `.pkl` files at every request, prediction latency will spike. Load once at startup and reuse.

```python
# app/ml/inference_server.py
from functools import lru_cache
import joblib

class InferenceServer:
    _instance = None
    _models: dict = {}

    @classmethod
    def get_instance(cls) -> "InferenceServer":
        """Singleton — models are loaded exactly once at first call."""
        if cls._instance is None:
            cls._instance = cls()
            cls._instance._load_all_models()
        return cls._instance

    def _load_all_models(self) -> None:
        self._models["gate_t10"] = joblib.load("app/ml/models/gate_load_t10.pkl")
        self._models["gate_t30"] = joblib.load("app/ml/models/gate_load_t30.pkl")
        self._models["departure"] = joblib.load("app/ml/models/departure_rf.pkl")
        self._models["anomaly"]   = joblib.load("app/ml/models/anomaly_iso_forest.pkl")

    def predict_gate_load(self, features: dict) -> dict:
        model_t10 = self._models["gate_t10"]
        model_t30 = self._models["gate_t30"]
        ...
```

**Issue 3.4 — Base64 images inflate memory and response time**

Storing 4K background images as Base64 in Firebase RTDB means every page load fetches and decodes a multi-MB string. Switch to Firebase Cloud Storage (proper blob storage) and serve via signed URLs.

```python
# app/services/asset_service.py
from firebase_admin import storage
from datetime import timedelta

def get_background_image_url(filename: str) -> str:
    """Return a time-limited signed URL for a background image in Cloud Storage."""
    bucket = storage.bucket()
    blob = bucket.blob(f"assets/{filename}")
    url = blob.generate_signed_url(expiration=timedelta(hours=1))
    return url
```

Then in Streamlit:

```python
# streamlit_app/utils/asset_loader.py
@st.cache_data(ttl=3600)
def get_background_url() -> str:
    return asset_service.get_background_image_url("stadium_background.jpg")
    # Returns a CDN-cached URL — browser handles loading, not Python
```

**Issue 3.5 — Google Maps embed should use a single static API call**

`maps_helper.py` currently generates embed URLs dynamically per render. Cache the Maps embed URL per gate since gate coordinates do not change.

```python
# streamlit_app/utils/maps_helper.py

@st.cache_data  # permanent cache — gate coordinates never change
def get_gate_map_embed_url(gate_id: str, lat: float, lon: float) -> str:
    """Generate Google Maps embed URL for a stadium gate. Cached permanently."""
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    return (
        f"https://www.google.com/maps/embed/v1/place"
        f"?key={api_key}&q={lat},{lon}&zoom=17"
    )
```

---

## Criterion 4: Testing

### What judges look for
Automated tests that can be run with a single command. Tests must cover the happy path, error conditions, and the ML layer.

### Issue 4.1 — Create a `tests/` directory with three layers

```
tests/
├── conftest.py             ← shared fixtures (test client, mock Firebase)
├── unit/
│   ├── test_models.py      ← Pydantic validation tests
│   ├── test_gate_service.py
│   └── test_ml_inference.py
├── integration/
│   ├── test_auth_routes.py
│   ├── test_booking_routes.py
│   └── test_food_routes.py
└── e2e/
    └── test_booking_flow.py ← full booking → gate assignment → notification
```

**`conftest.py` — shared test setup**

```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app

@pytest.fixture
def client():
    """FastAPI test client — no live Firebase connection needed."""
    return TestClient(app)

@pytest.fixture(autouse=True)
def mock_firebase(monkeypatch):
    """Mock all Firebase calls so tests run offline."""
    mock_db = MagicMock()
    mock_db.get.return_value = None
    mock_db.set.return_value = True
    monkeypatch.setattr("app.services.firebase_client.db", mock_db)
    return mock_db
```

**`test_models.py` — Pydantic validation**

```python
# tests/unit/test_models.py
import pytest
from pydantic import ValidationError
from app.models.ticket import BookingRequest

def test_valid_booking_request():
    req = BookingRequest(
        user_id="usr_001",
        event_id="evt_001",
        seat_zone="A",
        quantity=2,
        commute_mode="metro",
        group_size=2
    )
    assert req.seat_zone == "A"
    assert req.commute_mode == "metro"

def test_invalid_seat_zone_rejected():
    with pytest.raises(ValidationError) as exc:
        BookingRequest(
            user_id="usr_001", event_id="evt_001",
            seat_zone="Z",       # invalid
            quantity=1, commute_mode="metro", group_size=1
        )
    assert "seat_zone must be one of" in str(exc.value)

def test_quantity_out_of_range_rejected():
    with pytest.raises(ValidationError):
        BookingRequest(
            user_id="usr_001", event_id="evt_001",
            seat_zone="A",
            quantity=99,          # invalid — max is 10
            commute_mode="metro", group_size=1
        )
```

**`test_booking_routes.py` — API integration tests**

```python
# tests/integration/test_booking_routes.py
def test_create_booking_returns_201(client, mock_firebase):
    mock_firebase.get.return_value = {"name": "Test User", "email": "test@stadium.com"}

    response = client.post("/bookings/create", json={
        "user_id": "usr_001",
        "event_id": "evt_cricket_01",
        "seat_zone": "B",
        "quantity": 1,
        "commute_mode": "metro",
        "group_size": 1
    }, headers={"Authorization": "Bearer mock-valid-token"})

    assert response.status_code == 201
    data = response.json()
    assert "ticket_id" in data
    assert "gate_assigned" in data
    assert data["gate_assigned"] in ["A", "B", "C", "D"]

def test_booking_without_auth_returns_401(client):
    response = client.post("/bookings/create", json={
        "user_id": "usr_001", "event_id": "evt_001",
        "seat_zone": "A", "quantity": 1,
        "commute_mode": "bus", "group_size": 1
    })
    assert response.status_code == 401

def test_booking_with_invalid_zone_returns_422(client, mock_firebase):
    response = client.post("/bookings/create", json={
        "user_id": "usr_001", "event_id": "evt_001",
        "seat_zone": "Z",     # invalid
        "quantity": 1, "commute_mode": "metro", "group_size": 1
    }, headers={"Authorization": "Bearer mock-valid-token"})
    assert response.status_code == 422
```

**`test_ml_inference.py` — ML layer validation**

```python
# tests/unit/test_ml_inference.py
from app.ml.inference_server import InferenceServer

def test_inference_server_is_singleton():
    a = InferenceServer.get_instance()
    b = InferenceServer.get_instance()
    assert a is b  # same object — loaded once

def test_gate_load_prediction_returns_expected_shape():
    server = InferenceServer.get_instance()
    result = server.predict_gate_load({
        "gate_id": "A",
        "timestamp_minute": 5,
        "attendees_passed": 200,
        "weather": "clear",
        "event_type": "cricket",
        "day_of_week": 6
    })
    assert "predicted_queue_t10" in result
    assert "predicted_queue_t30" in result
    assert "should_proactive_reroute" in result
    assert isinstance(result["predicted_queue_t10"], (int, float))

def test_gate_prediction_flags_overflow():
    server = InferenceServer.get_instance()
    # Inject high-load features
    result = server.predict_gate_load({
        "gate_id": "A",
        "timestamp_minute": 10,
        "attendees_passed": 50,    # very few exited — gate blocked
        "weather": "rain",
        "event_type": "football",
        "day_of_week": 0
    })
    assert result["should_proactive_reroute"] is True
```

**Running all tests**

```bash
pip install pytest pytest-asyncio httpx

# Run all tests
pytest tests/ -v --tb=short

# Run only unit tests
pytest tests/unit/ -v

# Run with coverage report
pip install pytest-cov
pytest tests/ --cov=app --cov-report=term-missing
# Target: > 70% coverage before submission
```

---

## Criterion 5: Accessibility

### What judges look for
The solution should be usable by people with different abilities, devices, and language backgrounds. For a stadium system specifically, think: elderly users, first-time smartphone users, non-English speakers, users in poor lighting.

### Issue 5.1 — Add keyboard navigation and ARIA labels to Streamlit

Streamlit handles some accessibility natively, but critical interactive elements need explicit help.

```python
# streamlit_app/utils/ui_helper.py — inject accessible CSS
def inject_accessibility_css():
    st.markdown("""
    <style>
    /* High-contrast focus ring for keyboard navigation */
    button:focus, input:focus, select:focus {
        outline: 3px solid #FF6B00 !important;
        outline-offset: 2px;
    }

    /* Minimum touch target size (48x48px) for mobile stadium use */
    .stButton > button {
        min-height: 48px;
        min-width: 120px;
        font-size: 16px;   /* Prevents iOS zoom on tap */
    }

    /* Sufficient contrast for outdoor readability (WCAG AA: 4.5:1) */
    .stMarkdown p, .stMarkdown li {
        color: #1A1A1A;
        font-size: 16px;
        line-height: 1.6;
    }
    </style>
    """, unsafe_allow_html=True)
```

### Issue 5.2 — Add descriptive alt text to all images

```python
# Every image rendered via st.image() must have alt text
st.image(
    background_url,
    caption=None,
    use_column_width=True,
    # Streamlit does not support alt= natively, so wrap in HTML:
)

# Use this pattern for images with semantic meaning:
st.markdown(
    f'<img src="{background_url}" alt="Stadium aerial view showing Gate A, B, C and D locations" '
    f'style="width:100%;border-radius:8px;">',
    unsafe_allow_html=True
)
```

### Issue 5.3 — Add multi-language support for gate notifications

Indian stadiums serve audiences that may not be comfortable in English. A language selector on the home screen with at least Hindi support costs very little effort.

```python
# streamlit_app/utils/i18n.py
STRINGS = {
    "en": {
        "gate_assigned":       "Your assigned gate is Gate {gate}.",
        "gate_busy_warning":   "Gate {gate} is getting busy. Consider leaving now.",
        "food_order_ready":    "Your order will be ready in {minutes} minutes.",
        "sos_triggered":       "Emergency reported. Follow the green exit signs to Safe Exit {exit}.",
        "booking_confirmed":   "Booking confirmed! Ticket ID: {ticket_id}",
    },
    "hi": {
        "gate_assigned":       "आपका निर्धारित गेट {gate} है।",
        "gate_busy_warning":   "गेट {gate} व्यस्त हो रहा है। अभी निकलने पर विचार करें।",
        "food_order_ready":    "आपका ऑर्डर {minutes} मिनट में तैयार होगा।",
        "sos_triggered":       "आपातकाल की सूचना दी गई। हरे निकास संकेतों का पालन करें — सुरक्षित निकास {exit}।",
        "booking_confirmed":   "बुकिंग की पुष्टि हुई! टिकट आईडी: {ticket_id}",
    },
    "mr": {
        "gate_assigned":       "तुमचा नियुक्त गेट {gate} आहे।",
        "gate_busy_warning":   "गेट {gate} गर्दीने भरत आहे. आत्ता निघण्याचा विचार करा।",
        "food_order_ready":    "तुमची ऑर्डर {minutes} मिनिटांत तयार होईल।",
        "sos_triggered":       "आपत्कालीन घटना नोंदवली गेली. हिरव्या निर्गम चिन्हांचे अनुसरण करा — सुरक्षित निर्गम {exit}।",
        "booking_confirmed":   "बुकिंग यशस्वी झाली! तिकीट आईडी: {ticket_id}",
    }
}

def t(key: str, lang: str = "en", **kwargs) -> str:
    """Return a localised string, falling back to English if key missing."""
    template = STRINGS.get(lang, STRINGS["en"]).get(key, STRINGS["en"].get(key, key))
    return template.format(**kwargs)
```

Language selector on the home page:

```python
# streamlit_app/pages/01_home.py
lang = st.selectbox(
    "Language / भाषा / भाषा",
    options=["en", "hi", "mr"],
    format_func=lambda x: {"en": "English", "hi": "हिन्दी", "mr": "मराठी"}[x]
)
st.session_state["lang"] = lang
```

### Issue 5.4 — Error messages must be human-readable

Never expose raw Python exceptions or Firebase error codes to the user.

```python
# Before
st.error(str(e))   # shows: "400 Client Error: Bad Request for url: ..."

# After
FIREBASE_ERROR_MAP = {
    "EMAIL_EXISTS":           "This email is already registered. Please log in.",
    "INVALID_PASSWORD":       "Incorrect password. Please try again.",
    "USER_NOT_FOUND":         "No account found with this email.",
    "TOO_MANY_ATTEMPTS":      "Too many failed attempts. Please wait 5 minutes.",
}

def friendly_error(firebase_code: str, lang: str = "en") -> str:
    return FIREBASE_ERROR_MAP.get(firebase_code, "Something went wrong. Please try again.")
```

### Issue 5.5 — Offline-capable error state

Stadium Wi-Fi is unreliable. If the backend is unreachable, show a clear message rather than a white screen.

```python
# streamlit_app/utils/api_client.py
import requests
from requests.exceptions import ConnectionError, Timeout

def safe_get(url: str, timeout: int = 5) -> dict | None:
    """Make a GET request with graceful failure handling."""
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except (ConnectionError, Timeout):
        st.warning("Cannot reach the server. Check your connection and refresh.")
        return None
    except requests.HTTPError as e:
        st.error(f"Server error ({e.response.status_code}). Please try again shortly.")
        return None
```

---

## Criterion 6: Google Services

### What judges look for
Deep, meaningful integration — not just Firebase Auth bolted on. Show that GCP services are central to the solution's value, not cosmetic.

### Current integrations (confirmed working)
- Firebase Realtime Database — core persistence
- Firebase Authentication — user sessions
- Google Maps Embed API — gate and parking navigation
- Firebase RTDB for asset storage (backgrounds, GIFs)

### Issue 6.1 — Add Google Cloud Logging for observability

This is a one-line addition that makes your demo look production-grade. Every gate assignment, ML prediction, and anomaly gets logged to Cloud Logging, visible in GCP Console.

```bash
pip install google-cloud-logging
```

```python
# app/config/logging_config.py
import google.cloud.logging
import logging

def setup_cloud_logging():
    """Route Python logging to Google Cloud Logging."""
    client = google.cloud.logging.Client()
    client.setup_logging()
    logger = logging.getLogger("smart_stadium")
    return logger

# app/main.py
from app.config.logging_config import setup_cloud_logging
logger = setup_cloud_logging()

# Usage in gate_service.py
logger.info(f"Gate assigned: user={user_id}, gate={gate_id}, ml_score={score:.2f}")
logger.warning(f"Proactive reroute triggered: gate={gate_id}, predicted_queue={pred}")
```

Judges can open GCP Console → Cloud Logging and see every event in real time during the demo.

### Issue 6.2 — Add Vertex AI as a clear upgrade path (mention in demo)

The current ML layer uses scikit-learn and XGBoost running locally. Vertex AI is the natural GCP upgrade. You do not need to migrate now, but prepare one slide or admin panel note:

```python
# streamlit_app/pages/06_admin.py — add an info banner
st.info(
    "ML models currently run locally (XGBoost, scikit-learn). "
    "Production deployment uses Google Vertex AI for auto-scaling inference. "
    "See: cloud.google.com/vertex-ai"
)
```

Add to `requirements.txt` with a comment:

```
# google-cloud-aiplatform>=1.50   # Vertex AI — enable for cloud deployment
```

This shows the judges you know the GCP ecosystem beyond Firebase.

### Issue 6.3 — Use Firebase Cloud Messaging (FCM) for real push notifications

Currently notifications are in-app only (Streamlit session state). FCM enables real device push notifications — the most direct demonstration of GCP depth.

```python
# app/services/notification_service.py
from firebase_admin import messaging

def send_gate_notification(fcm_token: str, gate_id: str, queue_depth: int, lang: str = "en") -> bool:
    """Send a real push notification via Firebase Cloud Messaging."""
    message = messaging.Message(
        notification=messaging.Notification(
            title="Gate Update" if lang == "en" else "गेट अपडेट",
            body=t("gate_assigned", lang, gate=gate_id),
        ),
        data={
            "gate_id": gate_id,
            "queue_depth": str(queue_depth),
            "action": "navigate_to_gate"
        },
        token=fcm_token,
    )
    try:
        messaging.send(message)
        return True
    except Exception as e:
        logger.error(f"FCM send failed for token {fcm_token[:10]}...: {e}")
        return False
```

### Issue 6.4 — Deploy backend to Google Cloud Run

For the hackathon demo, running on `localhost:8000` is a single point of failure. Cloud Run gives a public HTTPS URL, zero cold-start issues, and impresses judges.

Create `Dockerfile` at project root:

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Deploy command:

```bash
gcloud run deploy smart-stadium-api \
  --source . \
  --region asia-south1 \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars FIREBASE_API_KEY=$FIREBASE_API_KEY,FIREBASE_DATABASE_URL=$FIREBASE_DATABASE_URL
```

The `asia-south1` region (Mumbai) gives the lowest latency for an Indian hackathon demo audience.

### Issue 6.5 — Add Google Maps Distance Matrix for walk-time estimates

Currently the gate information shows a gate name. Add actual walking time from seat to gate using the Maps Distance Matrix API.

```python
# streamlit_app/utils/maps_helper.py
import httpx

async def get_walk_time_minutes(
    from_lat: float, from_lon: float,
    to_lat: float, to_lon: float
) -> int:
    """Return walking time in minutes between two stadium coordinates."""
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    url = (
        f"https://maps.googleapis.com/maps/api/distancematrix/json"
        f"?origins={from_lat},{from_lon}"
        f"&destinations={to_lat},{to_lon}"
        f"&mode=walking"
        f"&key={api_key}"
    )
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
    
    data = resp.json()
    duration_seconds = data["rows"][0]["elements"][0]["duration"]["value"]
    return max(1, round(duration_seconds / 60))
```

Display in the user app:

```python
walk_time = get_walk_time_minutes(user_seat_lat, user_seat_lon, gate_lat, gate_lon)
st.metric("Walk to your gate", f"{walk_time} min")
```

---

## Final Pre-Submission Checklist

Run through every item below before submitting. Items marked BLOCKER will fail the submission if not done.

### Security (BLOCKER items first)

- [ ] **BLOCKER** — No API keys, service account JSON, or passwords in any `.py` or `.json` file
- [ ] **BLOCKER** — `.env` file is in `.gitignore` and `.env.example` is committed instead
- [ ] **BLOCKER** — Firebase token verified server-side on every protected route
- [ ] CORS restricted to specific origins (not `*`)
- [ ] Rate limiting on `/auth/login` and `/auth/register`
- [ ] All Pydantic models have field validators

### Code Quality

- [ ] All public functions have type hints and a one-line docstring
- [ ] Page files renamed to sequential descriptive names
- [ ] `flake8 app/ streamlit_app/` returns zero errors
- [ ] `firebase_config.py` contains only init logic, no CRUD
- [ ] `ui_helper.py` split into `ui_helper`, `asset_loader`, `animation_helper`
- [ ] `README.md` at project root with setup in 3 commands + test credentials

### Efficiency

- [ ] `@st.cache_data` applied to all static Firebase reads (events, assets, gate coords)
- [ ] All FastAPI route handlers are `async def`
- [ ] `InferenceServer` is a singleton — models loaded once at startup
- [ ] Background images served from Cloud Storage signed URLs, not RTDB Base64

### Testing

- [ ] `pytest tests/` runs without errors
- [ ] Tests cover: valid booking, auth rejection, invalid input (422), ML prediction shape
- [ ] `pytest --cov=app` reports > 70% coverage on `/services` and `/routes`
- [ ] `seed_test_users.py` runs cleanly on a fresh Firebase project

### Accessibility

- [ ] Focus ring CSS injected on every page via `ui_helper.py`
- [ ] Minimum button height 48px enforced via CSS
- [ ] Language selector (English / हिन्दी / मराठी) on home page
- [ ] All user-facing error messages use `friendly_error()`, not raw exceptions
- [ ] `safe_get()` used for all backend calls — graceful offline handling

### Google Services

- [ ] Google Cloud Logging configured — gate assignments and ML alerts visible in GCP Console
- [ ] FCM push notifications working for gate assignment events
- [ ] Backend deployed to Cloud Run (`asia-south1`) with a live HTTPS URL
- [ ] Vertex AI mentioned as upgrade path in admin panel and README
- [ ] Google Maps Distance Matrix used for walk-time estimates

---

## Execution Order (Time-boxed)

| Time block | Actions |
|---|---|
| First 2 hours | Secrets to `.env`, Firebase token middleware, CORS restriction (Security BLOCKERs) |
| Next 2 hours | Type hints + docstrings on all services, flake8 clean, file renaming (Code Quality) |
| Next 2 hours | `@st.cache_data` everywhere, async routes, singleton inference server (Efficiency) |
| Next 3 hours | Write and run `tests/` — aim for 70% coverage (Testing) |
| Next 2 hours | Accessibility CSS, language selector, `safe_get`, friendly errors (Accessibility) |
| Final 2 hours | Cloud Logging, Cloud Run deploy, FCM wiring, Maps Distance Matrix (Google Services) |
| Last 30 min | Run full checklist, seed test users on clean DB, do one complete demo walkthrough |
