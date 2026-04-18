#!/usr/bin/env python3
"""
Smart Stadium ML - Staff Effectiveness Dataset Generator

Pairs gate load levels with staff counts and measures throughput outcomes.
Usage: python generate_staff_logs.py --events 20 --output-dir data/generated
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


def calculate_throughput(peak_queue: int, staff_count: int, avg_time_sec: float) -> int:
    """
    Calculate realistic throughput per hour based on staff and queue depth.
    More staff → higher throughput. Crowded gates → slower per-person processing.
    """
    base_throughput = 60 / avg_time_sec  # People per minute
    staff_multiplier = 0.3 + (staff_count * 0.2)  # More staff → higher throughput
    queue_congestion_penalty = 1.0 - min(0.3, peak_queue / 500)  # Crowded → slower
    
    throughput_per_min = base_throughput * staff_multiplier * queue_congestion_penalty
    throughput_per_hour = throughput_per_min * 60
    
    return int(throughput_per_hour)


def generate_staff_logs(num_events: int) -> list:
    """Generate staff-to-outcome mapping data."""
    records = []
    
    for event_num in range(1, num_events + 1):
        event_id = f"EVT_{event_num:03d}"
        event_date = datetime.now() + timedelta(days=event_num)
        
        for gate in GATES:
            # Realistic staff allocations: 2-10 per gate
            staff_count = random.randint(2, 10)
            
            # Peak queue during event exit
            peak_queue = random.randint(80, 400)
            
            # Processing time per person (seconds): baseline 5-8 sec, varies with staff
            base_proc_time = 5 + (staff_count ** -0.3) * 3  # More staff → slightly slower check (thorough)
            avg_proc_time = base_proc_time + random.gauss(0, 0.5)
            avg_proc_time = max(3, min(12, avg_proc_time))  # Clamp to 3-12 sec
            
            # Calculate throughput
            throughput = calculate_throughput(peak_queue, staff_count, avg_proc_time)
            
            # Incidents: overworked staff → more incidents
            incident_prob = 0.1 + (peak_queue / 500) * 0.3
            incident_count = 1 if random.random() < incident_prob else 0
            
            record = {
                "event_id": event_id,
                "event_date": event_date.isoformat(),
                "gate_id": gate,
                "staff_count": staff_count,
                "peak_queue_depth": peak_queue,
                "avg_processing_time_sec": round(avg_proc_time, 2),
                "incident_count": incident_count,
                "throughput_per_hour": throughput,
                "efficiency_score": round(throughput / staff_count, 2)  # Throughput per staff member
            }
            records.append(record)
    
    return records


def save_dataset(records: list, output_dir: Path) -> None:
    """Save staff logs to CSV."""
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "staff_logs.csv"
    
    with open(output_file, 'w', newline='') as f:
        fieldnames = records[0].keys()
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)
    
    print(f"✓ Generated {len(records):,} staff effectiveness records")
    print(f"✓ Saved to: {output_file}")
    
    # Print summary stats
    print("\n📊 Dataset Summary:")
    avg_staff = np.mean([r['staff_count'] for r in records])
    avg_throughput = np.mean([r['throughput_per_hour'] for r in records])
    avg_efficiency = np.mean([r['efficiency_score'] for r in records])
    total_incidents = sum(r['incident_count'] for r in records)
    
    print(f"  Avg staff per gate: {avg_staff:.1f}")
    print(f"  Avg throughput: {avg_throughput:.0f} people/hour")
    print(f"  Avg efficiency: {avg_efficiency:.1f} people/hour per staff member")
    print(f"  Total incidents: {total_incidents}")
    print(f"  Avg processing time: {np.mean([r['avg_processing_time_sec'] for r in records]):.2f} sec")


def main():
    parser = argparse.ArgumentParser(description="Generate staff effectiveness logs")
    parser.add_argument("--events", type=int, default=20, help="Number of events")
    parser.add_argument("--output-dir", type=str, default="data/generated", help="Output directory")
    
    args = parser.parse_args()
    
    print(f"👥 Generating staff logs for {args.events} events (4 gates each)\n")
    
    records = generate_staff_logs(args.events)
    output_dir = Path(args.output_dir)
    save_dataset(records, output_dir)


if __name__ == "__main__":
    main()
