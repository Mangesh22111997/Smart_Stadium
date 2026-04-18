#!/usr/bin/env python3
"""
Smart Stadium ML - Attendee Dataset Generator

Generates realistic booking records with commute preferences and seat assignments.
Usage: python generate_attendees.py --events 20 --attendees-per-event 2500
"""

import json
import uuid
import random
from datetime import datetime, timedelta
from pathlib import Path
import argparse
from typing import List, Dict

# Set seed for reproducibility
random.seed(42)

# Realistic probability distributions
COMMUTE_MODE_DIST = {
    "metro": 0.35,
    "private_car": 0.25,
    "cab": 0.20,
    "bus": 0.15,
    "walk": 0.05
}

AGE_GROUP_DIST = {
    "18-25": 0.25,
    "26-40": 0.35,
    "41-60": 0.25,
    "60+": 0.15
}

DEPARTURE_PREF_DIST = {
    "early": 0.20,
    "at_whistle": 0.50,
    "linger": 0.30
}

EVENT_TYPES = ["cricket", "football", "concert"]
ZONES = ["A", "B", "C", "D"]
PARKING_ZONES = ["P1", "P2", "P3"]


def weighted_choice(distribution: Dict[str, float]) -> str:
    """Select item based on probability distribution."""
    items = list(distribution.keys())
    weights = list(distribution.values())
    return random.choices(items, weights=weights, k=1)[0]


def correlate_parking_with_commute(commute_mode: str) -> tuple[bool, str | None]:
    """Parking is only booked for private car commuters (with 70% probability)."""
    if commute_mode == "private_car" and random.random() < 0.70:
        return True, random.choice(PARKING_ZONES)
    return False, None


def correlate_departure_with_zone(zone: str, declared_pref: str) -> str:
    """
    Outer zones (C, D) tend to leave earlier.
    Adjust declared preference with zone bias.
    """
    zone_early_bias = {"A": 0.1, "B": 0.25, "C": 0.40, "D": 0.45}
    bias = zone_early_bias.get(zone, 0.1)
    
    if random.random() < bias and declared_pref != "early":
        return "early"
    return declared_pref


def generate_attendees(num_events: int, attendees_per_event: int) -> List[Dict]:
    """Generate attendee dataset with realistic correlations."""
    attendees = []
    
    for event_num in range(1, num_events + 1):
        event_id = f"EVT_{event_num:03d}"
        event_date = datetime.now() + timedelta(days=event_num)
        
        for _ in range(attendees_per_event):
            commute_mode = weighted_choice(COMMUTE_MODE_DIST)
            parking_booked, parking_zone = correlate_parking_with_commute(commute_mode)
            declared_pref = weighted_choice(DEPARTURE_PREF_DIST)
            zone = random.choice(ZONES)
            
            # Final departure preference (after zone correlation)
            final_pref = correlate_departure_with_zone(zone, declared_pref)
            
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
    
    return attendees


def save_dataset(attendees: List[Dict], output_dir: Path) -> None:
    """Save attendees to JSON file."""
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "attendees.json"
    
    with open(output_file, 'w') as f:
        json.dump(attendees, f, indent=2)
    
    print(f"✓ Generated {len(attendees):,} attendee records")
    print(f"✓ Saved to: {output_file}")
    
    # Print summary stats
    print("\n📊 Dataset Summary:")
    commute_counts = {}
    for attendee in attendees:
        mode = attendee['commute_mode']
        commute_counts[mode] = commute_counts.get(mode, 0) + 1
    
    for mode, count in sorted(commute_counts.items()):
        pct = (count / len(attendees)) * 100
        print(f"  {mode}: {count:,} ({pct:.1f}%)")


def main():
    parser = argparse.ArgumentParser(description="Generate attendee dataset for Smart Stadium ML")
    parser.add_argument("--events", type=int, default=20, help="Number of events to simulate")
    parser.add_argument("--attendees-per-event", type=int, default=2500, help="Attendees per event")
    parser.add_argument("--output-dir", type=str, default="data/generated", help="Output directory")
    
    args = parser.parse_args()
    
    print(f"🎫 Generating {args.events} events × {args.attendees_per_event} attendees/event = {args.events * args.attendees_per_event:,} total records\n")
    
    attendees = generate_attendees(args.events, args.attendees_per_event)
    output_dir = Path(args.output_dir)
    save_dataset(attendees, output_dir)


if __name__ == "__main__":
    main()
