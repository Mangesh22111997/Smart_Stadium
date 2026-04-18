#!/usr/bin/env python3
"""
Direct data generation - bypasses subprocess issues
Run with: .\.venv\Scripts\python run_data_gen.py
"""

import json
import uuid
import random
import csv
from datetime import datetime, timedelta
from pathlib import Path
import numpy as np

random.seed(42)
np.random.seed(42)

OUTPUT_DIR = Path("data/generated")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("\n" + "="*70)
print("  SMART STADIUM ML - DATA GENERATION")
print("="*70)

# ============================================================================
# PHASE 1: ATTENDEE DATASET
# ============================================================================
print("\n[1/4] Generating attendee dataset...")

COMMUTE_MODE_DIST = {"metro": 0.35, "private_car": 0.25, "cab": 0.20, "bus": 0.15, "walk": 0.05}
AGE_GROUP_DIST = {"18-25": 0.25, "26-40": 0.35, "41-60": 0.25, "60+": 0.15}
DEPARTURE_PREF_DIST = {"early": 0.20, "at_whistle": 0.50, "linger": 0.30}

def weighted_choice(distribution):
    items = list(distribution.keys())
    weights = list(distribution.values())
    return random.choices(items, weights=weights, k=1)[0]

attendees = []
num_events = 20
attendees_per_event = 2500

for event_num in range(1, num_events + 1):
    event_id = f"EVT_{event_num:03d}"
    event_date = datetime.now() + timedelta(days=event_num)
    
    for _ in range(attendees_per_event):
        commute_mode = weighted_choice(COMMUTE_MODE_DIST)
        
        # Parking only for private car (70% prob)
        if commute_mode == "private_car" and random.random() < 0.70:
            parking_booked = True
            parking_zone = random.choice(["P1", "P2", "P3"])
        else:
            parking_booked = False
            parking_zone = None
        
        zone = random.choice(["A", "B", "C", "D"])
        declared_pref = weighted_choice(DEPARTURE_PREF_DIST)
        
        # Zone correlation
        zone_early_bias = {"A": 0.1, "B": 0.25, "C": 0.40, "D": 0.45}
        if random.random() < zone_early_bias[zone] and declared_pref != "early":
            final_pref = "early"
        else:
            final_pref = declared_pref
        
        attendee = {
            "attendee_id": str(uuid.uuid4()),
            "event_id": event_id,
            "event_date": event_date.isoformat(),
            "seat_zone": zone,
            "seat_row": random.randint(1, 50),
            "commute_mode": commute_mode,
            "parking_booked": parking_booked,
            "parking_zone": parking_zone,
            "departure_preference": final_pref,
            "group_size": random.randint(1, 6),
            "age_group": weighted_choice(AGE_GROUP_DIST),
            "is_first_time": random.choice([True, False]),
            "ticket_price": random.choice([500, 750, 1000, 1500]),
            "booking_timestamp": (event_date - timedelta(days=random.randint(1, 30))).isoformat()
        }
        attendees.append(attendee)

with open(OUTPUT_DIR / "attendees.json", 'w') as f:
    json.dump(attendees, f)

print(f"✓ Generated {len(attendees):,} attendees")

# ============================================================================
# PHASE 2: GATE LOADS
# ============================================================================
print("[2/4] Generating gate load time-series...")

def poisson_peak_curve(t, peak_time=15, scale=1.0):
    distance_from_peak = abs(t - peak_time)
    base_height = 150 * scale * np.exp(-distance_from_peak / 20)
    return max(0, base_height + random.gauss(0, 10))

gate_loads = []
for event_num in range(1, num_events + 1):
    event_id = f"EVT_{event_num:03d}"
    event_date = datetime.now() + timedelta(days=event_num)
    event_type = random.choice(["cricket", "football", "concert"])
    weather = random.choice(["clear", "rain", "extreme"])
    day_of_week = event_date.weekday()
    
    for gate in ["A", "B", "C", "D"]:
        gate_scale = random.uniform(0.8, 1.2)
        rain_multiplier = 1.4 if weather == "rain" else (1.1 if weather == "extreme" else 1.0)
        cumulative_passed = 0
        
        for minute in range(-30, 91):
            base_queue = poisson_peak_curve(minute, peak_time=15, scale=gate_scale * rain_multiplier)
            queue_depth = max(0, int(base_queue + random.gauss(0, 5)))
            
            if minute <= 0:
                cumulative_passed = random.randint(200, 500)
            else:
                newly_passed = max(0, int(queue_depth * 0.3 + random.randint(20, 50)))
                cumulative_passed += newly_passed
            
            incidents = 1 if queue_depth > 200 else 0
            
            gate_loads.append({
                "event_id": event_id,
                "event_type": event_type,
                "gate_id": gate,
                "timestamp_minute": minute,
                "attendees_passed": cumulative_passed,
                "queue_depth": queue_depth,
                "incidents": incidents,
                "weather": weather,
                "day_of_week": day_of_week,
                "event_date": event_date.isoformat()
            })

with open(OUTPUT_DIR / "gate_loads.csv", 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=gate_loads[0].keys())
    writer.writeheader()
    writer.writerows(gate_loads)

print(f"✓ Generated {len(gate_loads):,} gate load records")

# ============================================================================
# PHASE 3: STAFF LOGS
# ============================================================================
print("[3/4] Generating staff effectiveness logs...")

def calculate_throughput(peak_queue, staff_count, avg_time_sec):
    base_throughput = 60 / avg_time_sec
    staff_multiplier = 0.3 + (staff_count * 0.2)
    queue_congestion_penalty = 1.0 - min(0.3, peak_queue / 500)
    throughput_per_min = base_throughput * staff_multiplier * queue_congestion_penalty
    return int(throughput_per_min * 60)

staff_logs = []
for event_num in range(1, num_events + 1):
    event_id = f"EVT_{event_num:03d}"
    event_date = datetime.now() + timedelta(days=event_num)
    
    for gate in ["A", "B", "C", "D"]:
        staff_count = random.randint(2, 10)
        peak_queue = random.randint(80, 400)
        base_proc_time = 5 + (staff_count ** -0.3) * 3
        avg_proc_time = base_proc_time + random.gauss(0, 0.5)
        avg_proc_time = max(3, min(12, avg_proc_time))
        
        throughput = calculate_throughput(peak_queue, staff_count, avg_proc_time)
        incident_prob = 0.1 + (peak_queue / 500) * 0.3
        incident_count = 1 if random.random() < incident_prob else 0
        
        staff_logs.append({
            "event_id": event_id,
            "event_date": event_date.isoformat(),
            "gate_id": gate,
            "staff_count": staff_count,
            "peak_queue_depth": peak_queue,
            "avg_processing_time_sec": round(avg_proc_time, 2),
            "incident_count": incident_count,
            "throughput_per_hour": throughput,
            "efficiency_score": round(throughput / staff_count, 2)
        })

with open(OUTPUT_DIR / "staff_logs.csv", 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=staff_logs[0].keys())
    writer.writeheader()
    writer.writerows(staff_logs)

print(f"✓ Generated {len(staff_logs):,} staff effectiveness records")

# ============================================================================
# PHASE 4: FOOD ORDERS
# ============================================================================
print("[4/4] Generating food order patterns...")

def demand_profile(minute):
    event_minute = minute + 30
    if event_minute < 0:
        return 0.2
    elif event_minute < 30:
        return 0.3 + (event_minute / 30) * 0.5
    elif event_minute < 45:
        return 0.8 + random.gauss(0, 0.1)
    elif event_minute < 60:
        peak = 0.9 + (event_minute - 45) / 15 * 0.8
        return min(1.8, peak + random.gauss(0, 0.15))
    elif event_minute < 90:
        return 0.75 + random.gauss(0, 0.1)
    elif event_minute < 150:
        tail_factor = (150 - event_minute) / 60
        result = 0.5 * tail_factor + random.gauss(0, 0.05)
        return max(0, result)
    else:
        return 0

zone_mult = {"A": 1.0, "B": 0.95, "C": 0.85, "D": 0.75}

food_orders = []
for event_num in range(1, num_events + 1):
    event_id = f"EVT_{event_num:03d}"
    event_date = datetime.now() + timedelta(days=event_num)
    
    for booth in [f"B{i}" for i in range(1, 9)]:
        zone = random.choice(["A", "B", "C", "D"])
        item_category = random.choice(["snack", "meal", "beverage"])
        booth_popularity = random.uniform(0.7, 1.3)
        
        for minute_offset in range(-30, 150):
            base_demand = demand_profile(minute_offset)
            zone_adj = zone_mult[zone]
            demand_factor = base_demand * booth_popularity * zone_adj
            
            order_count = int(max(0, np.random.poisson(demand_factor * 15)))
            base_wait = 2 + (order_count * 0.8)
            avg_wait_sec = base_wait + random.gauss(0, 1)
            avg_wait_sec = max(0, avg_wait_sec)
            
            food_orders.append({
                "event_id": event_id,
                "event_date": event_date.isoformat(),
                "booth_id": booth,
                "zone": zone,
                "item_category": item_category,
                "timestamp_minute": minute_offset,
                "order_count": order_count,
                "avg_wait_time_sec": round(avg_wait_sec, 1),
                "half_time": 45 <= (minute_offset + 30) <= 60
            })

with open(OUTPUT_DIR / "food_orders.csv", 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=food_orders[0].keys())
    writer.writeheader()
    writer.writerows(food_orders)

print(f"✓ Generated {len(food_orders):,} food order records")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "="*70)
print("  SUMMARY")
print("="*70)
print(f"✅ Attendees:      {len(attendees):,}")
print(f"✅ Gate Loads:     {len(gate_loads):,}")
print(f"✅ Staff Logs:     {len(staff_logs):,}")
print(f"✅ Food Orders:    {len(food_orders):,}")
print(f"\n📁 Output: {OUTPUT_DIR.absolute()}")
print("\n🎉 All datasets generated successfully!")
