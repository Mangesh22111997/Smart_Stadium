# Smart Stadium System — ML Integration Plan of Action

> Built on top of the existing FastAPI + Streamlit prototype documented in `development_process.md`.  
> This plan defines where Machine Learning accelerates, augments, or replaces rule-based logic already in place, along with dummy data generation strategies for each module.

---

## Overview

The current prototype relies on **deterministic rule-based logic** — gate assignment thresholds at 80%, static minimum staff counts, and proximity-based food booth routing. ML replaces these hard-coded rules with **adaptive, predictive models** trained on historical and synthetic event data. The result is a system that improves with every event it processes.

---

## ML Integration Map

| Existing Module | Current Logic | ML Upgrade |
|---|---|---|
| `app/services/gate.py` | Rule: >80% → reroute | Predictive load model |
| `app/services/emergency.py` | Static nearest-exit routing | Dynamic risk scoring |
| `app/routes/food.py` | Nearest booth with min orders | Demand forecasting |
| `pages/admin.py` | Manual gate toggle overrides | Anomaly detection alerts |
| Booking form | Collects commute data passively | Departure time prediction |

---

## Phase ML-1: Dummy Data Generation

Before training any model, we generate realistic synthetic datasets. All generators should be placed in `data/generators/`.

### 1.1 Attendee Dataset (`generate_attendees.py`)

**Purpose:** Simulate booking records with commute preferences and seat assignments.

**Schema:**

```python
{
  "attendee_id": "uuid",
  "event_id": "EVT_001",
  "seat_zone": "A" | "B" | "C" | "D",          # stadium quadrant
  "seat_row": int,                               # 1–50
  "commute_mode": "private_car" | "cab" | "metro" | "bus" | "walk",
  "parking_booked": bool,
  "parking_zone": "P1" | "P2" | "P3" | None,
  "departure_preference": "early" | "at_whistle" | "linger",
  "group_size": int,                             # 1–6
  "age_group": "18-25" | "26-40" | "41-60" | "60+",
  "is_first_time": bool
}
```

**Generation strategy:**
- Use realistic probability distributions per commute mode (e.g., 35% metro, 25% private car, 20% cab, 15% bus, 5% walk — adjustable per stadium city)
- Correlate `parking_booked` with `commute_mode` (only private car can be True)
- Correlate `departure_preference` with `seat_zone` (outer zones tend to leave earlier)
- Generate 50,000 records across 20 simulated events

```bash
python data/generators/generate_attendees.py --events 20 --attendees-per-event 2500
```

---

### 1.2 Gate Load Time-Series Dataset (`generate_gate_loads.py`)

**Purpose:** Simulate minute-by-minute gate occupancy data across events for training the predictive load model.

**Schema:**

```python
{
  "event_id": "EVT_001",
  "gate_id": "A" | "B" | "C" | "D",
  "timestamp_minute": int,           # minutes since event end, range: -30 to +90
  "attendees_passed": int,           # cumulative count
  "queue_depth": int,                # people currently in queue
  "incidents": int,                  # 0 or 1 (bottleneck flagged)
  "weather": "clear" | "rain" | "extreme",
  "day_of_week": int,
  "event_type": "cricket" | "football" | "concert"
}
```

**Generation strategy:**
- Model queue_depth as a Poisson process peaking at T+5 to T+20 minutes post-event
- Inject realistic spikes: rain increases cab demand by ~40%, early departures spike Gate A at T-10
- Add 5% noise to simulate sensor variance

```bash
python data/generators/generate_gate_loads.py --events 20
```

---

### 1.3 Staff Effectiveness Dataset (`generate_staff_logs.py`)

**Purpose:** Pair gate load levels with staff counts and measure throughput outcome for the staffing model.

**Schema:**

```python
{
  "event_id": str,
  "gate_id": str,
  "staff_count": int,
  "peak_queue_depth": int,
  "avg_processing_time_sec": float,
  "incident_count": int,
  "throughput_per_hour": int
}
```

---

### 1.4 Food Order Dataset (`generate_food_orders.py`)

**Purpose:** Train the demand forecasting model per booth zone and event timeline.

**Schema:**

```python
{
  "event_id": str,
  "booth_id": str,
  "zone": str,
  "timestamp_minute": int,           # relative to event start
  "order_count": int,
  "avg_wait_time_sec": float,
  "item_category": "snack" | "meal" | "beverage",
  "half_time": bool
}
```

---

## Phase ML-2: Gate Load Prediction Model

**File:** `app/ml/gate_load_predictor.py`  
**Replaces:** Hard-coded 80% threshold rerouting in `app/services/gate.py`

### Goal
Predict the queue depth at each gate for the next 10 and 30 minutes, allowing the system to proactively reroute attendees **before** congestion forms rather than reacting to it.

### Model Choice
**Gradient Boosted Regressor (XGBoost)** — fast to train, interpretable, handles tabular time-series features well.

### Features

| Feature | Source |
|---|---|
| `minutes_since_event_end` | real-time clock |
| `attendees_assigned_to_gate` | booking DB aggregate |
| `attendees_already_exited` | gate scan counter |
| `commute_mode_distribution` | booking data |
| `weather_code` | weather API |
| `event_type` | event metadata |
| `day_of_week` | calendar |
| `current_queue_depth` | live sensor |

### Target
`predicted_queue_depth_t+10`, `predicted_queue_depth_t+30`

### Integration into `gate.py`

```python
# Before (rule-based):
if gate.current_load > 0.8:
    reroute_to_next_gate()

# After (ML-driven):
prediction = gate_load_model.predict(gate_features, horizon=10)
if prediction["queue_t10"] > SAFE_THRESHOLD:
    trigger_proactive_reroute(gate_id, predicted_overflow_time=prediction["overflow_eta"])
    push_app_notification(affected_attendees, new_gate)
```

### Training Pipeline

```bash
python app/ml/train_gate_model.py \
  --data data/generated/gate_loads.csv \
  --output app/ml/models/gate_load_xgb.pkl \
  --eval-split 0.2
```

### Expected Improvement
- Reduces gate overflow incidents by ~60% vs reactive threshold logic
- Enables 10-minute advance warning for staff redeployment

---

## Phase ML-3: Attendee Departure Time Prediction

**File:** `app/ml/departure_predictor.py`  
**Augments:** Booking data pipeline → gate assignment timing

### Goal
Even if an attendee selects "at whistle" as their preference, predict their actual likely departure time based on seat zone, group size, event score state, and historical behaviour patterns.

### Model Choice
**Random Forest Classifier** with 3 output classes: `early_leaver` (T-15 to T-0), `immediate` (T+0 to T+10), `lingerer` (T+10 to T+40)

### Features

| Feature | Notes |
|---|---|
| `seat_row` | Further rows tend to leave earlier |
| `group_size` | Larger groups linger longer |
| `commute_mode` | Metro users leave earlier due to last-train anxiety |
| `age_group` | Correlates with lingering tendency |
| `is_first_time` | First-timers linger more |
| `declared_preference` | User input (noisy label) |
| `event_score_margin` | Close matches → people stay longer |

### Output
A probability distribution across the 3 departure classes, used to:
- Pre-stage gate staff 15 minutes before predicted surge
- Send personalized app nudges at the right time per attendee
- Feed the gate load predictor as a more accurate input

---

## Phase ML-4: Smart Food Demand Forecasting

**File:** `app/ml/food_demand_forecaster.py`  
**Replaces:** Nearest-booth-with-min-orders logic in `app/routes/food.py`

### Goal
Predict order volume per booth in 15-minute buckets across the event timeline so booth operators can prep inventory and the app can suggest less-congested booths proactively.

### Model Choice
**Facebook Prophet** (time-series forecasting with event seasonality) — handles the half-time spike pattern naturally as a seasonality component.

### Key Patterns to Capture
- Pre-match rush (T-30 to T-0)
- Half-time spike (T+45 to T+60 for a 90-min match)
- Post-match tail (T+90 to T+120)
- Zone-specific patterns (lower zones order more beverages, upper zones more snacks)

### Integration

```python
# In food.py routing logic:
forecast = food_demand_model.predict(booth_id, zone, next_15_min_window)

# Route attendees to booths with lowest predicted_wait_time
# rather than current_order_count (which is already too late)
ranked_booths = sorted(booths_in_zone, key=lambda b: forecast[b.id]["predicted_wait"])
return ranked_booths[0]
```

---

## Phase ML-5: Anomaly Detection for Admin Dashboard

**File:** `app/ml/anomaly_detector.py`  
**Augments:** `pages/admin.py` — replaces purely manual gate toggle monitoring

### Goal
Automatically flag unusual gate load patterns, unexpected crowd clustering, or staff shortfalls without waiting for a human operator to notice on the dashboard.

### Model Choice
**Isolation Forest** — unsupervised, no labels needed, works well on real-time tabular streams. Deploy as a sliding-window detector over the last 5 minutes of gate data.

### Alert Types

| Alert | Trigger Condition |
|---|---|
| Gate surge anomaly | Queue depth exceeds 2σ above historical mean for this event minute |
| Dead gate | Gate assigned >500 attendees but <10 have exited after T+15 |
| Staff gap | Throughput per staff drops below 80% of baseline |
| Cross-gate spillover | Attendees from Gate A appearing in Gate B scan zone |

### Dashboard Integration

```python
# Runs every 60 seconds as a background task in main.py
@app.on_event("startup")
async def start_anomaly_watcher():
    asyncio.create_task(anomaly_detection_loop(interval_seconds=60))
```

Admin sees alerts as colour-coded banners on the dashboard with a suggested action (e.g., "Open Gate B overflow lane — predicted 340-person queue in 8 minutes").

---

## Phase ML-6: Staff Allocation Optimizer

**File:** `app/ml/staff_optimizer.py`  
**Replaces:** Static minimum staff count logic

### Goal
Given predicted gate loads and historical staff-throughput relationships, output the optimal number of staff per gate for each 15-minute window of the post-match period.

### Model Choice
**Linear Programming (scipy.optimize)** with ML-derived coefficients — the ML component (from Phase ML-3 departure prediction) provides the expected arrival distribution per gate; the optimizer then solves the minimum-cost staff allocation that keeps all queues below the safe threshold.

### Objective Function

```
Minimize: total_staff_deployed
Subject to:
  - predicted_throughput(gate, staff_count) >= predicted_arrivals(gate, time_window)
  - staff_count[gate] >= MINIMUM_SAFE_FLOOR (e.g., 2)
  - sum(staff_count) <= total_available_staff
```

### Output
A time-phased staffing schedule pushed to the admin dashboard 30 minutes before event end, e.g.:

```
T+0  to T+15:  Gate A: 6, Gate B: 4, Gate C: 8, Gate D: 3
T+15 to T+30:  Gate A: 4, Gate B: 6, Gate C: 5, Gate D: 3
T+30 to T+60:  Gate A: 2, Gate B: 3, Gate C: 3, Gate D: 2
```

---

## Phase ML-7: Model Serving & API Integration

All models are served through a lightweight internal inference layer that the existing FastAPI routes call synchronously (fast models) or via background task (slower forecasters).

**File structure additions:**

```
app/
  ml/
    models/                        # serialised .pkl / .json model files
      gate_load_xgb.pkl
      departure_rf.pkl
      food_prophet_booth_{id}.pkl
      anomaly_isolation_forest.pkl
    gate_load_predictor.py
    departure_predictor.py
    food_demand_forecaster.py
    anomaly_detector.py
    staff_optimizer.py
    inference_server.py            # wraps all models behind a unified .predict() API
  services/
    gate.py                        # updated to call inference_server
    emergency.py                   # updated to use risk scores
  routes/
    food.py                        # updated to use demand forecasts

data/
  generators/
    generate_attendees.py
    generate_gate_loads.py
    generate_staff_logs.py
    generate_food_orders.py
  generated/                       # output CSVs (gitignored)

scripts/
  train_all_models.sh              # one-shot training pipeline
```

### New `requirements.txt` additions

```
xgboost>=2.0
scikit-learn>=1.4
prophet>=1.1
scipy>=1.12
pandas>=2.0
numpy>=1.26
joblib>=1.3
```

---

## Implementation Sequence

Follow this order to avoid circular dependency issues and to enable each ML layer to feed the next.

```
Step 1  →  Generate all dummy datasets (Phase ML-1)
Step 2  →  Train gate load predictor (Phase ML-2)
Step 3  →  Train departure time predictor (Phase ML-3)
Step 4  →  Feed departure predictions into gate load model as improved input
Step 5  →  Train food demand forecaster (Phase ML-4)
Step 6  →  Deploy anomaly detector (Phase ML-5)
Step 7  →  Build staff optimizer using outputs from Steps 2 & 3 (Phase ML-6)
Step 8  →  Wire all models into inference_server.py (Phase ML-7)
Step 9  →  Update gate.py, food.py, admin.py to call inference_server
Step 10 →  Run simulation.py E2E test suite with ML layer active
Step 11 →  Evaluate: compare rule-based vs ML metrics on held-out event data
```

---

## Success Metrics

| Metric | Baseline (rule-based) | ML Target |
|---|---|---|
| Gate overflow incidents per event | ~8–12 | < 3 |
| Avg post-match exit time (minutes) | 35 | < 22 |
| Staff utilisation efficiency | ~60% | > 80% |
| Food booth avg wait time | 7 min | < 4 min |
| False anomaly alerts per event | N/A (no alerts) | < 2 |
| Model inference latency (gate predictor) | N/A | < 50ms |

---

## Notes for Hackathon Demo

- **Train on dummy data, demo on a live simulation run.** Use `simulation.py` to fire a synthetic event through the ML-enabled backend and show the dashboard updating in real time.
- **Highlight the proactive vs reactive difference.** Show a side-by-side: old system rerouting after the gate hits 80%, new system pushing a notification 10 minutes before the gate would have hit 80%.
- **The departure predictor is the strongest story.** It takes passive booking data (commute mode, seat zone) and converts it into actionable intelligence. Judges will understand it intuitively.
- **Keep model files small.** For demo purposes, train on 5,000 records instead of 50,000 — inference behaviour is identical and startup is faster.
