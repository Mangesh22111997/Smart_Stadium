#!/usr/bin/env python3
"""
Smart Stadium ML - Food Order Dataset Generator

Generates demand patterns per booth, capturing half-time spikes and zone variations.
Usage: python generate_food_orders.py --events 20 --output-dir data/generated
"""

import random
import csv
from datetime import datetime, timedelta
from pathlib import Path
import argparse
import numpy as np

random.seed(42)
np.random.seed(42)

BOOTHS = ["B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8"]  # 8 food booths
ZONES = ["A", "B", "C", "D"]
ITEM_CATEGORIES = ["snack", "meal", "beverage"]
EVENT_DURATION = 120  # minutes (typical football match)


def demand_profile(minute: int, is_half_time: bool = False) -> float:
    """
    Model realistic food demand across event timeline.
    - Pre-match rush: T-30 to T-0
    - Half-time spike: T+45 to T+60 (PEAK)
    - Post-match tail: T+90 to T+120
    """
    # Normalize to event timeline (0-120 minutes)
    event_minute = minute + 30
    
    if event_minute < 0:  # Pre-match (parking, entry)
        return 0.2  # Minimal orders
    elif event_minute < 30:  # Pre-match rush
        return 0.3 + (event_minute / 30) * 0.5  # Ramp up to 0.8
    elif event_minute < 45:  # First half
        return 0.8 + random.gauss(0, 0.1)
    elif event_minute < 60:  # HALF-TIME SPIKE
        peak = 0.9 + (event_minute - 45) / 15 * 0.8  # Jump to 1.7x baseline
        return min(1.8, peak + random.gauss(0, 0.15))
    elif event_minute < 90:  # Second half
        return 0.75 + random.gauss(0, 0.1)
    elif event_minute < 150:  # Post-match tail
        tail_factor = (150 - event_minute) / 60
        return 0.5 * tail_factor + random.gauss(0, 0.05)
    else:
        return 0


def zone_multiplier(zone: str) -> float:
    """Zone preferences for food types (VIP vs general seating)."""
    return {"A": 1.0, "B": 0.95, "C": 0.85, "D": 0.75}[zone]


def generate_food_orders(num_events: int) -> list:
    """Generate realistic food order patterns."""
    records = []
    
    for event_num in range(1, num_events + 1):
        event_id = f"EVT_{event_num:03d}"
        event_date = datetime.now() + timedelta(days=event_num)
        
        for booth in BOOTHS:
            # Each booth has a zone preference and item specialty
            zone = random.choice(ZONES)
            item_category = random.choice(ITEM_CATEGORIES)
            booth_popularity = random.uniform(0.7, 1.3)  # Some booths more popular
            
            for minute_offset in range(-30, 150):  # -30 to +150 minutes
                # Base demand from timeline profile
                base_demand = demand_profile(minute_offset)
                
                # Zone×popularity adjustment
                zone_adj = zone_multiplier(zone)
                demand_factor = base_demand * booth_popularity * zone_adj
                
                # Convert to actual order count (Poisson-like)
                order_count = int(max(0, np.random.poisson(demand_factor * 15)))
                
                # Wait time increases with orders
                base_wait = 2 + (order_count * 0.8)
                avg_wait_sec = base_wait + random.gauss(0, 1)
                avg_wait_sec = max(0, avg_wait_sec)
                
                record = {
                    "event_id": event_id,
                    "event_date": event_date.isoformat(),
                    "booth_id": booth,
                    "zone": zone,
                    "item_category": item_category,
                    "timestamp_minute": minute_offset,
                    "order_count": order_count,
                    "avg_wait_time_sec": round(avg_wait_sec, 1),
                    "half_time": 45 <= (minute_offset + 30) <= 60  # Half-time window
                }
                records.append(record)
    
    return records


def save_dataset(records: list, output_dir: Path) -> None:
    """Save food orders to CSV."""
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "food_orders.csv"
    
    with open(output_file, 'w', newline='') as f:
        fieldnames = records[0].keys()
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)
    
    print(f"✓ Generated {len(records):,} food order records")
    print(f"✓ Saved to: {output_file}")
    
    # Print summary stats
    print("\n📊 Dataset Summary:")
    total_orders = sum(r['order_count'] for r in records)
    avg_wait = np.mean([r['avg_wait_time_sec'] for r in records])
    peak_orders = max(r['order_count'] for r in records)
    half_time_records = [r for r in records if r['half_time']]
    half_time_orders = sum(r['order_count'] for r in half_time_records) if half_time_records else 0
    
    print(f"  Total orders across all records: {total_orders:,}")
    print(f"  Avg wait time: {avg_wait:.1f} sec")
    print(f"  Peak order count (single booth×minute): {peak_orders}")
    print(f"  Half-time spike orders: {half_time_orders} (out of {total_orders})")
    print(f"  Booths: {len(set(r['booth_id'] for r in records))}")
    print(f"  Events: {len(set(r['event_id'] for r in records))}")


def main():
    parser = argparse.ArgumentParser(description="Generate food order demand patterns")
    parser.add_argument("--events", type=int, default=20, help="Number of events")
    parser.add_argument("--output-dir", type=str, default="data/generated", help="Output directory")
    
    args = parser.parse_args()
    
    print(f"🍔 Generating food orders for {args.events} events (8 booths each)\n")
    
    records = generate_food_orders(args.events)
    output_dir = Path(args.output_dir)
    save_dataset(records, output_dir)


if __name__ == "__main__":
    main()
