#!/usr/bin/env python3
"""Inspect all data in a FIT file."""

import os
import sys
import glob

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fitparse import FitFile


def inspect_file(filepath):
    print(f"\n{'=' * 60}")
    print(f"FILE: {os.path.basename(filepath)}")
    print(f"{'=' * 60}")

    fitfile = FitFile(filepath)

    # Get all message types
    print("\n--- MESSAGE TYPES FOUND ---")
    message_types = set()
    for msg in fitfile.get_messages():
        message_types.add(msg.name)
    for mt in sorted(message_types):
        count = sum(1 for _ in fitfile.get_messages(mt))
        print(f"  {mt}: {count} messages")

    # Session summary
    print("\n--- SESSION DATA ---")
    for msg in fitfile.get_messages("session"):
        print(f"  Timestamp: {msg.get_value('timestamp')}")
        print(f"  Start Time: {msg.get_value('start_time')}")
        print(f"  Sport: {msg.get_value('sport')}")
        print(f"  Sub Sport: {msg.get_value('sub_sport')}")
        print(f"  Duration (elapsed): {msg.get_value('total_elapsed_time')} sec")
        print(f"  Duration (timer): {msg.get_value('total_timer_time')} sec")
        print(f"  Distance: {msg.get_value('total_distance')} m")
        print(f"  Calories: {msg.get_value('total_calories')}")
        print(f"  Avg HR: {msg.get_value('avg_heart_rate')}")
        print(f"  Max HR: {msg.get_value('max_heart_rate')}")
        print(f"  Avg Power: {msg.get_value('avg_power')}")
        print(f"  Max Power: {msg.get_value('max_power')}")
        print(f"  Avg Cadence: {msg.get_value('avg_cadence')}")
        print(f"  Max Cadence: {msg.get_value('max_cadence')}")
        print(f"  Training Stress Score: {msg.get_value('training_stress_score')}")
        print(f"  Intensity Factor: {msg.get_value('intensity_factor')}")
        print(f"  Normalized Power: {msg.get_value('normalized_power')}")
        print(f"  Avg Speed: {msg.get_value('avg_speed')} m/s")
        print(f"  Max Speed: {msg.get_value('max_speed')} m/s")
        print(f"  Avg Temperature: {msg.get_value('avg_temperature')} C")
        print(f"  Total Ascent: {msg.get_value('total_ascent')} m")
        print(f"  Total Descent: {msg.get_value('total_descent')} m")
        print(f"  Avg Vertical Speed: {msg.get_value('avg_vertical_speed')}")

    # Laps
    print("\n--- LAPS ---")
    for i, msg in enumerate(fitfile.get_messages("lap")):
        print(f"  Lap {i + 1}:")
        print(f"    Start: {msg.get_value('start_time')}")
        print(f"    Duration: {msg.get_value('total_elapsed_time')} sec")
        print(f"    Distance: {msg.get_value('total_distance')} m")
        print(f"    Avg HR: {msg.get_value('avg_heart_rate')}")
        print(f"    Max HR: {msg.get_value('max_heart_rate')}")

    # Records (time series) - sample first 5 and last 5
    print("\n--- TIME SERIES RECORDS (sample) ---")
    records = list(fitfile.get_messages("record"))
    print(f"  Total records: {len(records)}")

    if records:
        print("  First 3 records:")
        for msg in records[:3]:
            ts = msg.get_value("timestamp")
            hr = msg.get_value("heart_rate")
            speed = msg.get_value("speed")
            power = msg.get_value("power")
            cadence = msg.get_value("cadence")
            print(f"    {ts}: HR={hr}, Speed={speed}, Power={power}, Cadence={cadence}")

        if len(records) > 6:
            print("  ...")
            print("  Last 3 records:")
            for msg in records[-3:]:
                ts = msg.get_value("timestamp")
                hr = msg.get_value("heart_rate")
                speed = msg.get_value("speed")
                power = msg.get_value("power")
                cadence = msg.get_value("cadence")
                print(
                    f"    {ts}: HR={hr}, Speed={speed}, Power={power}, Cadence={cadence}"
                )

    # Events
    print("\n--- EVENTS ---")
    for msg in fitfile.get_messages("event"):
        print(
            f"  {msg.get_value('timestamp')}: {msg.get_value('event')} - {msg.get_value('event_type')}"
        )

    # Device info
    print("\n--- DEVICE INFO ---")
    for msg in fitfile.get_messages("device_info"):
        print(f"  Manufacturer: {msg.get_value('manufacturer')}")
        print(f"  Product: {msg.get_value('product_name') or msg.get_value('product')}")
        print(f"  Serial: {msg.get_value('serial_number')}")

    # Activity info
    print("\n--- ACTIVITY INFO ---")
    for msg in fitfile.get_messages("activity"):
        print(f"  Type: {msg.get_value('type')}")
        print(f"  Event: {msg.get_value('event')}")
        print(f"  Event Type: {msg.get_value('event_type')}")
        print(f"  Local Timestamp: {msg.get_value('local_timestamp')}")
        print(f"  Num Sessions: {msg.get_value('num_sessions')}")


def main():
    fit_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fit_files")
    fit_files = glob.glob(os.path.join(fit_dir, "*.fit"))

    if not fit_files:
        print("No .fit files found in fit_files/ directory")
        return

    for filepath in fit_files:
        inspect_file(filepath)


if __name__ == "__main__":
    main()
