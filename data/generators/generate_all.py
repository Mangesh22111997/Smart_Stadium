#!/usr/bin/env python3
"""
Smart Stadium ML - Master Data Generation Script

Runs all data generators in sequence to create complete synthetic dataset.
Usage: python data/generators/generate_all.py --events 20
"""

import subprocess
import sys
from pathlib import Path
import argparse


def run_generator(script_name: str, args: list) -> bool:
    """Run a generator script and check for success."""
    script_path = Path(__file__).parent / script_name
    
    print(f"\n{'='*70}")
    print(f"Running: {script_name}")
    print(f"{'='*70}")
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)] + args,
            check=True,
            capture_output=False
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {script_name} failed with exit code {e.returncode}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Generate all synthetic datasets for Smart Stadium ML")
    parser.add_argument("--events", type=int, default=20, help="Number of events to simulate")
    parser.add_argument("--attendees-per-event", type=int, default=2500, help="Attendees per event")
    parser.add_argument("--output-dir", type=str, default="data/generated", help="Output directory")
    
    args = parser.parse_args()
    
    print("\n" + "="*70)
    print("  SMART STADIUM ML - SYNTHETIC DATA GENERATION")
    print("="*70)
    print(f"\nConfiguration:")
    print(f"  Events: {args.events}")
    print(f"  Attendees/event: {args.attendees_per_event}")
    print(f"  Total attendees: {args.events * args.attendees_per_event:,}")
    print(f"  Output directory: {args.output_dir}")
    
    generators = [
        ("generate_attendees.py", [
            "--events", str(args.events),
            "--attendees-per-event", str(args.attendees_per_event),
            "--output-dir", args.output_dir
        ]),
        ("generate_gate_loads.py", [
            "--events", str(args.events),
            "--output-dir", args.output_dir
        ]),
        ("generate_staff_logs.py", [
            "--events", str(args.events),
            "--output-dir", args.output_dir
        ]),
        ("generate_food_orders.py", [
            "--events", str(args.events),
            "--output-dir", args.output_dir
        ]),
    ]
    
    results = {}
    for script, script_args in generators:
        results[script] = run_generator(script, script_args)
    
    print("\n" + "="*70)
    print("  SUMMARY")
    print("="*70)
    for script, success in results.items():
        status = "✅ DONE" if success else "❌ FAILED"
        print(f"{status}: {script}")
    
    all_success = all(results.values())
    if all_success:
        print("\n🎉 All datasets generated successfully!")
        print(f"📁 Output directory: {args.output_dir}")
        return 0
    else:
        print("\n⚠️  Some generators failed. Check output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
