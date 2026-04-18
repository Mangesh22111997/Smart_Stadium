#!/usr/bin/env python3
"""
Smart Stadium ML - Gate Load Time-Series Dataset Generator

Generates minute-by-minute gate occupancy data for training the predictive load model.
Usage: python generate_gate_loads.py --events 20 --output-dir data/generated
"""

import json
import random
import csv
from datetime import datetime, timedelta
from pathlib import Path
import argparse
import numpy as np

random.seed(42)
np.random.seed(42)

GATES = ["A", "B", "C", "D"]
EVENT_TYPES = ["cricket", "football", "concert"]
WEATHER_TYPES = ["clear", "rain", "extreme"]
TIME_RANGE = range(-30, 91)  # -30 to +90 minutes relative to event end


def poisson_peak_curve(t: int, peak_time: int = 15, scale: float = 1.0) -> float:
    """Model queue depth as Poisson process peaking at T+15 minutes."""
    # Peak at event end (T=0), with secondary peaks before/after
    distance_from_peak = abs(t - peak_time)
    base_height = 150 * scale * np.exp(-distance_from_peak / 20)
    return max(0, base_height + random.gauss(0, 10))


def generate_gate_loads(num_events: int) -> list:
    """Generate realistic gate load time-series data."""
    records = []
    
    for event_num in range(1, num_events + 1):
        event_id = f"EVT_{event_num:03d}"
        event_date = datetime.now() + timedelta(days=event_num)
        event_type = random.choice(EVENT_TYPES)
        weather = random.choice(WEATHER_TYPES)
        day_of_week = event_date.weekday()
        
        for gate in GATES:
            # Each gate has slightly different load profile
            gate_scale = random.uniform(0.8, 1.2)
            rain_multiplier = 1.4 if weather == "rain" else (1.1 if weather == "extreme" else 1.0)
            
            cumulative_passed = 0
            
            for minute in TIME_RANGE:
                # Queue depth follows Poisson-like distribution
                base_queue = poisson_peak_curve(minute, peak_time=15, scale=gate_scale * rain_multiplier)
                queue_depth = max(0, int(base_queue + random.gauss(0, 5)))
                
                # Attendees passed is cumulative if queue is clearing
                if minute <= 0:
                    cumulative_passed = random.randint(200, 500)
                else:
                    newly_passed = max(0, int(queue_depth * 0.3 + random.randint(20, 50)))
                    cumulative_passed += newly_passed
                
                # Incidents: flag if queue unexpectedly high
                incidents = 1 if queue_depth > 200 else 0
                
                record = {
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
                }
                records.append(record)
    
    return records


def save_dataset(records: list, output_dir: Path) -> None:
    """Save gate load data to CSV."""
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "gate_loads.csv"
    
    # Write CSV
    with open(output_file, 'w', newline='') as f:
        fieldnames = records[0].keys()
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)
    
    print(f"✓ Generated {len(records):,} gate load records")
    print(f"✓ Saved to: {output_file}")
    
    # Print summary
    print("\n📊 Dataset Summary:")
    print(f"  Time range: -30 to +90 minutes")
    print(f"  Gates: {len(set(r['gate_id'] for r in records))}")
    print(f"  Events: {len(set(r['event_id'] for r in records))}")
    print(f"  Avg queue depth: {np.mean([r['queue_depth'] for r in records]):.1f}")
    print(f"  Max queue depth: {max(r['queue_depth'] for r in records)}")
    print(f"  Incident records: {sum(r['incidents'] for r in records)}")


def main():
    parser = argparse.ArgumentParser(description="Generate gate load time-series dataset")
    parser.add_argument("--events", type=int, default=20, help="Number of events")
    parser.add_argument("--output-dir", type=str, default="data/generated", help="Output directory")
    
    args = parser.parse_args()
    
    print(f"📈 Generating gate load time-series for {args.events} events\n")
    
    records = generate_gate_loads(args.events)
    output_dir = Path(args.output_dir)
    save_dataset(records, output_dir)


if __name__ == "__main__":
    main()
