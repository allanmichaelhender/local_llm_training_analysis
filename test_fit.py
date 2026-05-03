#!/usr/bin/env python3
"""Quick test for FIT file parsing."""

import os
import sys
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.fit_processor import FITProcessor

def main():
    print("🔧 Testing FIT Processor")
    print("-" * 40)

    # Initialize processor
    processor = FITProcessor()

    # Check device connection
    print(f"Device connected: {processor.is_device_connected()}")
    print(f"Activity path: {processor.activity_path}")

    if not processor.is_device_connected():
        print("\n⚠️  No Garmin device detected.")
        print("   Connect your device or place .fit files in:")
        print("   - D:/Garmin/Activity")
        print("   - E:/Garmin/Activity")
        print("   - Or set GARMIN_ACTIVITY_PATH env var")
        return

    # Look for files from last 7 days
    since = datetime.now() - timedelta(days=7)
    print(f"\n📁 Scanning for files since {since.strftime('%Y-%m-%d')}")

    new_files = processor.find_new_files(since)
    print(f"   Found {len(new_files)} file(s)")

    # Parse first file as demo
    for filepath in new_files[:3]:  # Test first 3
        print(f"\n📄 {os.path.basename(filepath)}")
        activity = processor.parse_file(filepath)

        if activity:
            print(f"   Type: {activity['type']}")
            print(f"   Duration: {activity['duration_minutes']:.1f} min")
            print(f"   Distance: {activity['distance_km']:.2f} km")
            print(f"   Avg HR: {activity['avg_hr']}")
            print(f"   Calories: {activity['calories']}")
        else:
            print("   ❌ Failed to parse")

    print("\n✅ Test complete")

if __name__ == "__main__":
    main()
