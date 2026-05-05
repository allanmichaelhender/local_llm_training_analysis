"""
Test script for Garmin Connect MCP integration.
Tests the new GarminClient and GarminHRAggregator services.
"""

from services.garmin_client import GarminClient
from services.garmin_hr_aggregator import GarminHRAggregator


def test_garmin_client():
    """Test GarminClient functionality."""
    print("Testing Garmin Client...")
    print("=" * 50)

    garmin = GarminClient()

    # Test 1: Get latest activity
    print("\n1. Testing get_latest_activity()...")
    activity = garmin.get_latest_activity()
    if activity:
        print(f"✓ Found activity: {activity['type']} - {activity['title']}")
        print(f"  ID: {activity['id']}")
        print(f"  Duration: {activity['duration_minutes']:.1f} min")
        print(f"  Distance: {activity['distance_km']:.2f} km")
        print(f"  Avg HR: {activity['avg_hr']}")
        print(f"  Max HR: {activity['max_hr']}")
    else:
        print("✗ No activity found")
        return False

    # Test 2: Extract HR time series
    print("\n2. Testing extract_hr_time_series()...")
    activity_id = int(activity["id"])
    hr_time_series = garmin.extract_hr_time_series(activity_id)
    if hr_time_series:
        print(f"✓ Extracted {len(hr_time_series)} HR data points")
        print(f"  First sample: {hr_time_series[0]}")
        print(f"  Last sample: {hr_time_series[-1]}")
    else:
        print("✗ No HR data extracted")
        return False

    # Test 3: Aggregate HR data
    print("\n3. Testing GarminHRAggregator...")
    hr_aggregator = GarminHRAggregator(bucket_seconds=10)
    hr_buckets = hr_aggregator.aggregate_hr_data(hr_time_series)
    if hr_buckets:
        print(f"✓ Aggregated into {len(hr_buckets)} buckets")
        print(f"  First bucket: {hr_buckets[0]}")
        print(f"  Last bucket: {hr_buckets[-1]}")
        print(f"  Data reduction: {len(hr_time_series)} → {len(hr_buckets)} samples")
    else:
        print("✗ HR aggregation failed")
        return False

    # Test 4: HR summary stats
    print("\n4. Testing get_hr_summary_stats()...")
    stats = hr_aggregator.get_hr_summary_stats(hr_time_series)
    if stats:
        print(f"✓ HR Statistics:")
        print(f"  Min HR: {stats['min_hr']}")
        print(f"  Max HR: {stats['max_hr']}")
        print(f"  Avg HR: {stats['avg_hr']:.1f}")
        print(f"  Sample count: {stats['sample_count']}")
    else:
        print("✗ HR statistics failed")
        return False

    print("\n" + "=" * 50)
    print("✓ All tests passed!")
    return True


if __name__ == "__main__":
    try:
        success = test_garmin_client()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
