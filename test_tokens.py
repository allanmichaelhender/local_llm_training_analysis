#!/usr/bin/env python3
"""
Simple test for Strava tokens without Unicode issues.
"""

import os
from dotenv import load_dotenv
from services.strava_client import StravaClient

load_dotenv()


def test_tokens():
    print("Strava Token Test")
    print("=" * 40)

    client = StravaClient()

    # Test authentication
    print("Testing authentication...")
    if client.authenticate():
        print("Authentication successful!")
    else:
        print("Authentication failed")
        return False

    # Test activity fetching
    print("\nTesting activity fetching...")
    from datetime import datetime, timedelta

    since = datetime.now() - timedelta(days=7)
    activities = client.get_activities_since(since)

    print(f"Found {len(activities)} activities since {since.strftime('%Y-%m-%d')}")

    if activities:
        print("\nRecent activities:")
        for i, activity in enumerate(activities[:3]):
            print(f"  {i + 1}. {activity['type']} - {activity['title']}")
            print(f"     Duration: {activity['duration_minutes']:.1f} min")
            print(f"     Distance: {activity['distance_km']:.2f} km")

        print("Strava API working!")
        return True
    else:
        print("No activities found")
        return False


if __name__ == "__main__":
    success = test_tokens()
    if success:
        print("\nReady to run orchestrator.py")
    else:
        print("\nCheck token permissions")
