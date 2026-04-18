# Smart Stadium System — Master Plan of Action
### Combined & Augmented from Copilot + Gemini Development Tracks

> **Version**: 2.0 — Unified  
> **Date**: April 15, 2026  
> **Status**: Prototype Complete → Hardening & Feature Extension Phase  
> **Stack**: FastAPI · Streamlit · XGBoost · Prophet · Isolation Forest · scikit-learn

---

## 1. What Each Track Built (Honest Comparison)

Before defining what comes next, it is important to understand what each AI-assisted development track produced and where each one is stronger.

| Dimension | Copilot Track | Gemini Track | Winner |
|---|---|---|---|
| Microservice count | 11 services | 4–5 services | Copilot |
| Auth system | SHA256 + users.json + sessions | Not present | Copilot |
| ML models trained | XGBoost (T+10, T+30) — R²=0.955 | XGBoost + RF + Prophet + IsoForest | Gemini |
| Inference server | Yes — lazy-loaded, <50ms | Yes — single wrapper | Copilot |
| Frontend richness | 8 user + 7 admin features, Plotly | 5-tab flow, session state | Copilot |
| Admin anomaly UI | Red `st.error` banner from IsoForest | Described but not wired | Gemini (design) |
| Data generated | 50K attendees, 9680 gate rows, 28.8K food rows | 40K attendees, gate, food, staff | Copilot |
| Food demand model | Static nearest-booth only | Prophet (half-time seasonality) | Gemini |
| Departure predictor | Not present | RandomForest (early/whistle/linger) | Gemini |
| Staff optimizer | Manual allocation UI only | LP + ML coefficients (designed) | Gemini |
| Emergency routing | Nearest safe exit algorithm | Same | Tie |
| Documentation | Highly detailed with code snippets | High-level conceptual | Copilot |

**Conclusion**: The Copilot track has the stronger, more complete backend and frontend. The Gemini track has the more complete ML vision. The master plan below merges the Copilot codebase as the foundation and grafts in the Gemini ML additions that are missing.

---

## 2. Unified Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                      SMART STADIUM SYSTEM v2.0                       │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────────────┐          ┌───────────────────────────────────┐
│  STREAMLIT FRONTEND  │          │        FASTAPI BACKEND             │
│  (Port 8503)         │◄────────►│        (Port 8000)                 │
│                      │          │                                    │
│ • Auth / Login       │          │  11 Microservices (Copilot base)  │
│ • User Dashboard     │          │  + 3 New ML-backed routes          │
│ • Admin Portal       │          │  (departure, food forecast, staff) │
│ • Journey Tracker    │          │                                    │
│ • Emergency SOS      │          └───────────────────────────────────┘
│ • Notifications      │                          │
└──────────────────────┘                          ▼
                                  ┌───────────────────────────────────┐
                                  │         ML INFERENCE LAYER         │
                                  │                                    │
                                  │  • GateLoadPredictor (XGBoost)    │
                                  │    T+10 R²=0.955, T+30            │
                                  │  • DeparturePredictor (RF)  [NEW] │
                                  │  • FoodDemandForecaster           │
                                  │    (Prophet)               [NEW]  │
                                  │  • AnomalyDetector                │
                                  │    (Isolation Forest)      [NEW]  │
                                  │  • StaffOptimizer (LP+ML)  [NEW]  │
                                  │  • inference_server.py            │
                                  └───────────────────────────────────┘
                                                  │
                                                  ▼
                                  ┌───────────────────────────────────┐
                                  │         DATA & PERSISTENCE         │
                                  │                                    │
                                  │  • users.json / admins.json       │
                                  │  • In-memory caches (fast_db)     │
                                  │  • Generated CSVs (training)      │
                                  │  • SHA256 auth                    │
                                  └───────────────────────────────────┘
```

---

## 3. Current State Inventory

### 3.1 What Is Fully Built and Working

- FastAPI backend with 11 routes + services + Pydantic models
- XGBoost gate load prediction (T+10 and T+30), R²=0.955, <50ms inference
- Inference server with lazy-loading and model cache
- Streamlit frontend: 8 user features + 7 admin features
- SHA256 authentication, 5,000 pre-seeded attendees, 2 admin accounts
- Synthetic data: 50K attendees, 9,680 gate time-series rows, 28,800 food orders, 80 staff logs
- Real-time gate scoring formula: utilization (40%) + ML prediction (40%) + commute bonus (10%) + departure bonus (10%)
- Emergency SOS → nearest safe exit routing
- Broadcast notification system
- All integration tests passing (`test_ml_integration.py`)

### 3.2 What Was Designed but Not Yet Implemented

From the Gemini track, these ML modules were architecturally defined but not wired into the running codebase:

- `DeparturePredictor` — RandomForest classifying early/at-whistle/linger
- `FoodDemandForecaster` — Prophet with half-time seasonality
- `AnomalyDetector` — Isolation Forest on sliding 5-minute gate windows
- `StaffOptimizer` — LP solver using ML-derived arrival distributions
- Proactive push notification (T-15 pre-event-end nudge to attendees)
- Gate assignment sensitivity analysis for partial pre-registration

---

## 4. Plan of Action — Phased Execution

---

### Phase 1: Codebase Consolidation (Day 1)

**Goal**: Merge both tracks into a single clean repository before adding anything new.

#### Steps

1. Use the Copilot track (`Hack2Skill_Google_Challenge_copilot`) as the canonical base — it has the more complete backend and auth system.

2. Copy the following from the Gemini track into the Copilot base:
   - `data/generators/generate_attendees.py` — keep the Copilot version (50K records) but add Gemini's `departure_preference` and `age_group` fields to the schema, which are needed by the RF model.
   - `data/generators/generate_food_orders.py` — add Gemini's half-time boolean flag (`"half_time": bool`) to the schema.
   - ML model designs from `development_process.md` (departure predictor, food forecaster, anomaly detector, staff optimizer).

3. Standardise the `inference_server.py` — the Copilot version has the right structure, but add four new `predict_*` stubs matching the Gemini model designs.

4. Verify all existing tests still pass after merge.

**Deliverable**: Single repository, all Copilot functionality intact, new ML stubs in place and ready to implement.

---

### Phase 2: Complete the ML Layer (Days 2–4)

Implement the four missing models from the Gemini design. Each follows the same pattern: regenerate data → train → plug into inference_server → wire into the relevant service.

---

#### 2A. Departure Time Predictor

**File**: `app/ml/train_departure_model.py`  
**Model**: RandomForestClassifier  
**Output classes**: `early_leaver` | `immediate` | `lingerer`

First, regenerate attendees with the extra fields needed:

```bash
python data/generators/generate_attendees.py \
  --events 20 --attendees-per-event 2500 \
  --include-departure-label  # adds actual_departure_class column
```

Feature set for training:

| Feature | Why it matters |
|---|---|
| `seat_row` | Rows 40–50 leave 10 min earlier on average |
| `group_size` | Groups of 4+ tend to linger |
| `commute_mode` | Metro users leave early (last-train anxiety) |
| `age_group` | 60+ and families leave earliest |
| `is_first_time` | First-timers linger ~8 min longer |
| `declared_preference` | Noisy but useful input signal |
| `event_score_margin` | Close games keep people seated |

Training script outline:

```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib, pandas as pd

df = pd.read_json("data/generated/attendees.json")
X = df[FEATURE_COLS]
y = df["actual_departure_class"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
model = RandomForestClassifier(n_estimators=200, max_depth=10, random_state=42)
model.fit(X_train, y_train)
print(classification_report(y_test, model.predict(X_test)))
joblib.dump(model, "app/ml/models/departure_rf.pkl")
```

**Wiring into gate_service.py**: Feed the predicted departure distribution as an additional feature into the existing XGBoost gate load model, replacing the static `departure_preference` field.

**Wiring into notification_service.py**: At T-20 minutes before event end, call `predict_departure_class` for all registered attendees. Send personalised push to `immediate` and `early_leaver` segments: *"Your gate is Gate B — head there now to beat the rush."*

---

#### 2B. Food Demand Forecaster

**File**: `app/ml/train_food_model.py`  
**Model**: Facebook Prophet, one model per booth zone (A, B, C, D)

Regenerate food orders with richer time-series structure:

```bash
python data/generators/generate_food_orders.py \
  --events 20 --booths-per-zone 3 \
  --include-halftime-spike
```

Prophet captures three natural seasonality components in stadium food data:
- Pre-match rush (T-30 to T-0): beverages peak
- Half-time spike (T+45 to T+60 for 90-min matches): everything peaks simultaneously
- Post-match tail (T+90 to T+120): snacks and takeaways only

Training per zone:

```python
from prophet import Prophet
import pandas as pd, joblib

for zone in ["A", "B", "C", "D"]:
    df_zone = df[df["zone"] == zone][["ds", "y"]]  # ds=timestamp, y=order_count
    model = Prophet(seasonality_mode="multiplicative",
                    changepoint_prior_scale=0.05)
    model.add_seasonality(name="halftime", period=90/1440, fourier_order=3)
    model.fit(df_zone)
    joblib.dump(model, f"app/ml/models/food_prophet_{zone}.pkl")
```

**Wiring into food_service.py**: Replace the current nearest-booth-with-min-orders logic. Instead:

```python
# Before: static routing based on current order count
# After: predict wait time for next 15-min window, route to lowest predicted wait

forecast = inference_server.predict_food_demand(booth_id, zone, window_minutes=15)
ranked_booths = sorted(available_booths, key=lambda b: forecast[b.id]["predicted_wait_sec"])
return ranked_booths[0]
```

**Admin dashboard addition**: Add a "Food forecast" panel showing the predicted order surge curve for the next 60 minutes, colour-coded by booth zone.

---

#### 2C. Anomaly Detector

**File**: `app/ml/anomaly_detector.py`  
**Model**: Isolation Forest (unsupervised, no labels required)  
**Data needed**: existing `gate_loads.csv` (already generated)

The detector runs as a FastAPI background task on a 60-second loop, evaluating a sliding 5-minute window of gate metrics.

```python
from sklearn.ensemble import IsolationForest
import joblib, numpy as np

FEATURES = ["queue_depth", "attendees_passed", "throughput_rate",
            "staff_count", "incidents_last_5min"]

model = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
model.fit(X_normal)  # train on non-incident periods only
joblib.dump(model, "app/ml/models/anomaly_iso_forest.pkl")
```

Alert types and their actions:

| Alert | Detection condition | Automated action |
|---|---|---|
| Gate surge | Queue > 2σ above historical mean | Trigger proactive reroute for next 200 bookings |
| Dead gate | >500 assigned, <10 exited at T+15 | Page nearest staff supervisor |
| Staff gap | Throughput/staff < 80% of baseline | Staff optimizer recommends redeployment |
| Cross-gate spillover | Gate A attendees scanning at Gate B | Admin banner + manual override prompt |

**Wiring into main.py** (startup background task):

```python
@app.on_event("startup")
async def start_anomaly_watcher():
    asyncio.create_task(anomaly_detection_loop(interval_seconds=60))

async def anomaly_detection_loop(interval_seconds):
    while True:
        for gate_id in ["A", "B", "C", "D"]:
            features = get_live_gate_features(gate_id)
            score = inference_server.score_anomaly(features)  # returns -1 or 1
            if score == -1:
                await notification_service.broadcast_staff_alert(gate_id)
                await gate_service.flag_anomaly(gate_id)
        await asyncio.sleep(interval_seconds)
```

**Admin UI**: The existing `st.error()` anomaly banner in the Gemini design is the right pattern. Wire it to poll `/gates/anomaly/status` every 30 seconds via `st.rerun()`.

---

#### 2D. Staff Optimizer

**File**: `app/ml/staff_optimizer.py`  
**Approach**: Linear programming (scipy.optimize) with ML-derived input distributions

The optimizer runs once at T-30 minutes before event end, using departure predictor outputs as arrival forecasts per gate.

```python
from scipy.optimize import linprog
import numpy as np

def optimize_staff_allocation(predicted_arrivals_per_gate: dict,
                               total_staff_available: int,
                               time_windows: int = 3):
    """
    Minimize total staff deployed while keeping all queues below threshold.
    
    predicted_arrivals_per_gate: {gate_id: [arrivals_t0, arrivals_t15, arrivals_t30]}
    """
    THROUGHPUT_PER_STAFF = 120  # attendees/hour per staff member
    MIN_STAFF_PER_GATE = 2
    gates = ["A", "B", "C", "D"]
    
    # Build LP: minimise sum(staff), subject to throughput constraints
    # ... (full LP formulation)
    
    return schedule  # {gate: [staff_t0, staff_t15, staff_t30]}
```

Output pushed to admin dashboard as a time-phased schedule 30 minutes before event end:

```
Recommended staff schedule (generated at T-30):

         T+0–T+15   T+15–T+30   T+30–T+60
Gate A      6           4           2
Gate B      4           6           3
Gate C      8           5           3
Gate D      3           3           2
─────────────────────────────────────────
Total      21          18          10
```

---

### Phase 3: Backend Hardening (Days 3–5)

The Copilot backend is functionally complete but uses in-memory storage and JSON files. Before a hackathon demo or any real event, two areas need hardening.

#### 3A. Persistence Layer Upgrade

Currently: `users.json`, `admins.json`, and in-memory `fake_db` dicts.

**Recommended upgrade for hackathon**: SQLite via SQLAlchemy (zero infra, file-based, survives restarts).

```python
# Add to requirements.txt
sqlalchemy>=2.0
aiosqlite>=0.19

# Create app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./stadium.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

This ensures that if the server restarts mid-demo, all registrations, bookings, and gate assignments are preserved.

#### 3B. Authentication Upgrade

Currently: SHA256 password hashing with plain session state.

**Recommended upgrade**: Add JWT tokens using `python-jose`. This makes the API properly stateless and allows the frontend to authenticate against admin vs user roles cleanly.

```bash
pip install python-jose[cryptography] passlib[bcrypt]
```

```python
# app/utils/auth_utils.py additions
def create_access_token(data: dict, role: str, expires_minutes: int = 60):
    payload = {**data, "role": role, "exp": datetime.utcnow() + timedelta(minutes=expires_minutes)}
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def verify_token_role(token: str, required_role: str) -> bool:
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    return payload.get("role") == required_role
```

#### 3C. Weather API Integration

The gate load XGBoost model accepts a `weather` feature but currently defaults to `"clear"`. Add a real weather call so the model uses accurate input:

```python
# app/services/weather_service.py
import httpx

async def get_current_weather(lat: float, lon: float) -> str:
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
    code = resp.json()["current_weather"]["weathercode"]
    if code in range(61, 68) or code in range(80, 83):
        return "rain"
    elif code >= 71:
        return "extreme"
    return "clear"
```

Open-Meteo is free, no API key required — ideal for a hackathon.

---

### Phase 4: Frontend Enhancements (Days 4–5)

The Copilot frontend is well-built. These additions close the remaining UX gaps.

#### 4A. Commute Information Collection in Booking Flow

Currently the ticket booking tab collects: event, zone, quantity.

**Add to the booking form**:

```python
# In the booking tab of streamlit_app.py
with st.expander("Travel & Commute Details", expanded=True):
    commute_mode = st.selectbox(
        "How will you travel to/from the venue?",
        ["Metro / Local Train", "Personal/Private Car", "Cab (Ola/Uber)", "Bus", "Walk / Cycle"]
    )
    if commute_mode == "Personal/Private Car":
        parking_needed = st.checkbox("I need stadium parking")
        if parking_needed:
            parking_zone = st.selectbox("Preferred parking zone", ["P1 (North)", "P2 (South)", "P3 (East)"])
    
    departure_pref = st.radio(
        "When do you plan to leave?",
        ["Before final whistle (beat the crowd)", "Right at the end", "I'll take my time"]
    )
    group_size = st.number_input("How many people in your group?", min_value=1, max_value=20, value=1)
```

This data feeds directly into the gate scoring formula and the departure predictor.

#### 4B. Proactive Exit Notification Panel

Add a sidebar panel that activates in the last 20 minutes of the event:

```python
# Dynamic sidebar notification
if event_ending_soon:  # based on event_time from session_state
    st.sidebar.markdown("---")
    st.sidebar.warning("Event ending soon!")
    assigned_gate = st.session_state.get("assigned_gate")
    gate_queue = requests.get(f"{API_BASE_URL}/gates/{assigned_gate}/status").json()
    
    st.sidebar.metric("Your gate", assigned_gate)
    st.sidebar.metric("Current queue", f"{gate_queue['current_queue']} people")
    st.sidebar.metric("Predicted in 10 min", f"{gate_queue['predicted_t10']} people")
    
    if gate_queue['predicted_t10'] > THRESHOLD:
        st.sidebar.error(f"Gate {assigned_gate} will be busy — consider leaving now.")
    else:
        st.sidebar.success("Your gate is clear — good time to head out.")
```

#### 4C. Admin Food Forecast Panel

Add to `pages/admin.py`:

```python
# Food demand forecast chart
st.subheader("Food Booth Demand Forecast")
forecast_data = requests.get(f"{API_BASE_URL}/food/forecast?zone=all&window=60").json()
fig = px.line(forecast_data, x="timestamp", y="predicted_orders",
              color="booth_id", title="Expected orders — next 60 minutes")
st.plotly_chart(fig, use_container_width=True)
```

#### 4D. Staff Schedule Display

Add to admin portal:

```python
st.subheader("Recommended Staff Schedule")
schedule = requests.get(f"{API_BASE_URL}/staff/optimized-schedule").json()
df_schedule = pd.DataFrame(schedule)
st.dataframe(df_schedule.style.background_gradient(cmap="Reds"), use_container_width=True)
```

---

### Phase 5: New API Endpoints Required

Add these endpoints to support the Phase 2–4 additions. Each maps to a new route + service pair.

```
POST   /gates/assign-with-commute     ← Accepts commute fields from booking form
GET    /gates/anomaly/status          ← Returns anomaly scores for all gates
GET    /gates/{gate_id}/status        ← Live queue + ML prediction for sidebar

POST   /ml/predict-departure          ← RF departure class for a given attendee
GET    /food/forecast                 ← Prophet forecast for next N minutes
GET    /staff/optimized-schedule      ← LP-generated time-phased staff plan

POST   /notifications/proactive-exit  ← Triggered at T-20 event end
```

---

### Phase 6: Testing & Demo Preparation (Day 5–6)

#### 6A. Simulation Script Upgrade

Update `simulation.py` to exercise the new ML endpoints:

```python
# Test the full ML-augmented booking flow
def test_ml_booking_flow():
    # 1. Register user
    user = register_user(...)
    
    # 2. Book ticket WITH commute data
    ticket = book_ticket_with_commute(user.id, commute_mode="metro", departure_pref="at_whistle")
    assert ticket.gate_assigned in ["A", "B", "C", "D"]
    
    # 3. Verify ML prediction ran
    ml_status = get_gate_ml_status(ticket.gate_assigned)
    assert ml_status["model_used"] == "xgboost_t10"
    
    # 4. Trigger anomaly scenario
    inject_high_load(gate="A", queue_depth=850)
    time.sleep(65)  # wait for background loop
    anomaly_status = get_anomaly_status("A")
    assert anomaly_status["score"] == -1
    assert anomaly_status["alert_sent"] == True
```

#### 6B. Hackathon Demo Script (5-Minute Walkthrough)

Follow this exact sequence to show maximum value in minimum time:

| Minute | What to show | Why it impresses |
|---|---|---|
| 0:00–0:45 | Open booking form, fill commute details, book ticket → gate assigned | Shows the core concept immediately |
| 0:45–1:30 | Show gate assignment logic: ML score breakdown in admin | Demonstrates proactive vs reactive |
| 1:30–2:30 | Inject a high-load scenario on Gate A via admin override → anomaly alert fires → reroute notification | The "wow moment" — real-time ML in action |
| 2:30–3:15 | Show food demand forecast chart — half-time spike visible | Prophet seasonality is visually compelling |
| 3:15–4:00 | Show staff schedule table — auto-generated 30 min before event end | Operational value for venue managers |
| 4:00–5:00 | SOS flow: user triggers emergency → nearest safe exit shown | Safety + completeness |

#### 6C. Performance Targets to Verify Before Demo

```bash
# Run all checks
python test_ml_integration.py    # Must output: ALL TESTS PASSED
python simulation.py             # Must complete without errors

# Manual latency checks
curl -w "\nTime: %{time_total}s\n" http://localhost:8000/gates/ml/A
# Expected: < 0.050s

curl -w "\nTime: %{time_total}s\n" http://localhost:8000/food/forecast?zone=A&window=15
# Expected: < 0.200s (Prophet is slower, acceptable)
```

---

## 5. Add-Ons Beyond Both Tracks

These features were not in either development track but would meaningfully strengthen the system and are achievable within the hackathon timeframe.

### 5A. QR Code Gate Pass

When a ticket is confirmed, generate a QR code embedding `{ticket_id}:{gate_id}:{departure_window}`. Display it in the app. At the physical gate, staff scan it — no app lookup required.

```bash
pip install qrcode[pil]
```

```python
import qrcode
from io import BytesIO

def generate_gate_qr(ticket_id: str, gate_id: str) -> bytes:
    qr = qrcode.make(f"{ticket_id}|{gate_id}|{datetime.now().isoformat()}")
    buf = BytesIO()
    qr.save(buf, format="PNG")
    return buf.getvalue()
```

### 5B. Gate Load Sensitivity Analysis

A one-page section in the admin portal showing: *"At 50% pre-registration, gate overflow risk is X. At 90%, it drops to Y."* This is the single most convincing analytical piece for judges who ask "what if your app adoption is low?"

```python
# Pre-compute sensitivity table
reg_rates = [0.3, 0.5, 0.7, 0.9]
for rate in reg_rates:
    simulated_overflow_incidents = simulate_event(pre_registration_rate=rate)
    sensitivity_table.append({"registration_rate": rate,
                               "overflow_incidents": simulated_overflow_incidents})
```

### 5C. Offline Ticket Holder Gate Assignment

Currently, paper/kiosk ticket holders have no gate assignment. Add a kiosk endpoint that accepts seat zone and commute mode at entry time and returns the optimal gate in real-time, exactly as the app does.

```
POST /kiosk/gate-assign
Body: { "seat_zone": "B", "commute_mode": "bus", "group_size": 2 }
Response: { "gate": "D", "queue_current": 120, "walk_time_min": 3 }
```

### 5D. Multi-Language Notification Support

For Indian stadiums specifically, gate notifications in Hindi or Marathi alongside English would be a differentiated feature. Use a simple locale map:

```python
GATE_MESSAGES = {
    "en": "Head to Gate {gate} — {walk_time} min walk from your seat.",
    "hi": "गेट {gate} पर जाएं — आपकी सीट से {walk_time} मिनट की दूरी।",
    "mr": "गेट {gate} कडे जा — तुमच्या आसनापासून {walk_time} मिनिटांचे अंतर।"
}
```

---

## 6. Complete Updated File Structure

```
Smart_Stadium_System_v2/
├── app/
│   ├── main.py
│   ├── database.py                      [NEW — SQLite via SQLAlchemy]
│   ├── routes/
│   │   ├── user_routes.py
│   │   ├── ticket_routes.py             [UPDATED — commute fields]
│   │   ├── gate_routes.py               [UPDATED — anomaly + proactive endpoints]
│   │   ├── crowd_routes.py
│   │   ├── food_routes.py               [UPDATED — forecast endpoint]
│   │   ├── emergency_routes.py
│   │   ├── notification_routes.py       [UPDATED — proactive exit push]
│   │   ├── reassignment_routes.py
│   │   ├── orchestration_routes.py
│   │   ├── staff_dashboard_routes.py    [UPDATED — optimized schedule endpoint]
│   │   ├── booth_allocation_routes.py
│   │   └── kiosk_routes.py              [NEW — offline gate assignment]
│   ├── services/
│   │   ├── user_service.py
│   │   ├── ticket_service.py            [UPDATED — commute stored]
│   │   ├── gate_service.py              [UPDATED — anomaly + departure feeder]
│   │   ├── crowd_service.py
│   │   ├── food_service.py              [UPDATED — Prophet routing]
│   │   ├── emergency_service.py
│   │   ├── notification_service.py      [UPDATED — proactive + multilingual]
│   │   ├── reassignment_service.py
│   │   ├── orchestration_service.py
│   │   ├── staff_dashboard_service.py   [UPDATED — LP schedule]
│   │   ├── booth_allocation_service.py
│   │   └── weather_service.py           [NEW — Open-Meteo integration]
│   ├── models/
│   │   ├── user.py
│   │   ├── ticket.py                    [UPDATED — commute fields]
│   │   ├── gate.py                      [UPDATED — anomaly score field]
│   │   ├── crowd.py
│   │   ├── food.py
│   │   ├── emergency.py
│   │   ├── notification.py
│   │   └── orchestration.py
│   ├── ml/
│   │   ├── inference_server.py          [UPDATED — 4 new predict_ methods]
│   │   ├── train_gate_model.py
│   │   ├── train_departure_model.py     [NEW]
│   │   ├── train_food_model.py          [NEW]
│   │   ├── anomaly_detector.py          [NEW]
│   │   ├── staff_optimizer.py           [NEW]
│   │   └── models/
│   │       ├── gate_load_t10.pkl
│   │       ├── gate_load_t30.pkl
│   │       ├── gate_encoders.pkl
│   │       ├── gate_features.pkl
│   │       ├── departure_rf.pkl         [NEW]
│   │       ├── food_prophet_A.pkl       [NEW]
│   │       ├── food_prophet_B.pkl       [NEW]
│   │       ├── food_prophet_C.pkl       [NEW]
│   │       ├── food_prophet_D.pkl       [NEW]
│   │       └── anomaly_iso_forest.pkl   [NEW]
│   └── utils/
│       ├── auth_utils.py                [UPDATED — JWT]
│       └── qr_utils.py                  [NEW]
├── data/
│   ├── generators/
│   │   ├── generate_attendees.py        [UPDATED — departure_label field]
│   │   ├── generate_gate_loads.py
│   │   ├── generate_staff_logs.py
│   │   └── generate_food_orders.py      [UPDATED — half_time flag]
│   └── generated/
│       ├── attendees.json
│       ├── gate_loads.csv
│       ├── staff_logs.csv
│       └── food_orders.csv
├── scripts/
│   └── train_all_models.sh              [UPDATED — includes new models]
├── streamlit_app.py                     [UPDATED — commute form + exit sidebar]
├── pages/
│   └── admin.py                         [UPDATED — food forecast + staff schedule]
├── simulation.py                        [UPDATED — ML anomaly + departure tests]
├── test_ml_integration.py
├── requirements.txt
├── stadium.db                           [NEW — SQLite file]
└── README.md
```

---

## 7. Updated Requirements

```
# Backend
fastapi>=0.110
uvicorn>=0.29
pydantic>=2.6
python-jose[cryptography]>=3.3      # JWT [NEW]
passlib[bcrypt]>=1.7                # bcrypt hashing [NEW]
sqlalchemy>=2.0                     # SQLite ORM [NEW]
aiosqlite>=0.19                     # async SQLite [NEW]
httpx>=0.27                         # async HTTP (weather API) [NEW]

# ML
xgboost>=2.0
scikit-learn>=1.4
prophet>=1.1                        # [NEW]
scipy>=1.12                         # LP optimizer [NEW]
pandas>=2.0
numpy>=1.26
joblib>=1.3

# Frontend
streamlit>=1.33
plotly>=5.21
streamlit-option-menu>=0.3

# Utilities
qrcode[pil]>=7.4                    # QR gate pass [NEW]
requests>=2.31
```

---

## 8. Success Metrics (Revised)

| Metric | Baseline (rule-based) | Copilot Track (current) | v2.0 Target |
|---|---|---|---|
| Gate overflow incidents/event | 8–12 | ~3–4 (XGBoost) | < 2 |
| Avg post-match exit time | 35 min | ~22 min | < 18 min |
| Staff utilisation efficiency | ~60% | ~70% (manual) | > 85% (LP optimizer) |
| Food booth avg wait | 7 min | ~5 min (proximity) | < 3.5 min (Prophet) |
| Anomaly detection | 0 (none) | 0 (none) | < 2 false positives/event |
| ML gate inference latency | N/A | < 50ms | < 50ms (maintained) |
| Pre-event gate notification timing | Reactive | T+0 (at overflow) | T-10 (proactive) |
| System accuracy (XGBoost R²) | N/A | 0.955 | 0.955+ |

---

## 9. Execution Priority Order

If time is limited before the hackathon submission, execute in this strict priority:

1. **Phase 1 (Consolidation)** — non-negotiable, everything else depends on it
2. **Phase 4A (Commute form in booking)** — directly demonstrates your core concept to judges
3. **Phase 2C (Anomaly Detector)** — highest visual impact in the demo, fires a red banner
4. **Phase 2A (Departure Predictor)** — feeds better data into the existing gate model
5. **Phase 4B (Proactive exit sidebar)** — closes the user-facing story end-to-end
6. **Phase 2B (Food Forecaster)** — strong analytical demo piece
7. **Phase 3A (SQLite persistence)** — prevents embarrassing restarts during demo
8. **Phase 5A (QR Code)** — quick win, visually convincing
9. **Phase 2D (Staff Optimizer)** — useful but the LP formulation takes time
10. **Phase 5B (Sensitivity analysis)** — strongest analytical defence against tough questions
