"""
Garmin Connect client for fetching activity data.
Uses python-garminconnect library directly.
"""

import os
from typing import List, Dict, Optional

try:
    from garminconnect import Garmin
except ImportError:
    Garmin = None


class GarminClient:
    """Garmin Connect client using python-garminconnect library."""

    def __init__(self):
        """Initialize Garmin client."""
        if Garmin is None:
            raise ImportError(
                "python-garminconnect not installed. "
                "Install with: pip install garminconnect"
            )

        self._last_error = None
        self.garmin = None
        self._authenticated = False

    def _authenticate(self):
        """Authenticate with Garmin Connect."""
        if self._authenticated:
            return True

        email = os.getenv("GARMIN_EMAIL")
        password = os.getenv("GARMIN_PASSWORD")

        if not email or not password:
            raise Exception(
                "GARMIN_EMAIL and GARMIN_PASSWORD environment variables required"
            )

        try:
            print("   Authenticating with Garmin Connect...")
            self.garmin = Garmin(email, password)
            self.garmin.login()
            self._authenticated = True
            print("   Authentication successful")
            return True
        except Exception as e:
            raise Exception(f"Authentication failed: {e}")

    def get_activities(self, limit: int = 20) -> List[Dict]:
        """
        Get recent activities from Garmin Connect.

        Args:
            limit: Number of activities to return (1-100, default 20)

        Returns:
            List of complete raw activity dictionaries from Garmin
        """
        try:
            print(f"   Fetching {limit} most recent Garmin activities")
            self._authenticate()

            activities = self.garmin.get_activities(0, limit)

            if not activities:
                print("   No Garmin activities found")
                return []

            # Return raw activities
            for activity in activities:
                print(
                    f"Found: {activity.get('activityType', {}).get('typeKey', 'unknown')} - {activity.get('activityName', '')}"
                )

            return activities

        except Exception as e:
            print(f"Error fetching Garmin activities: {e}")
            self._last_error = str(e)
            return []

    def get_activity_details(self, activity_id: int) -> Optional[Dict]:
        """
        Get detailed activity metrics including HR time series data.

        Args:
            activity_id: Garmin activity ID

        Returns:
            Dictionary with detailed metrics including HR data
        """
        try:
            print(f"   Fetching details for activity {activity_id}")
            self._authenticate()
            details = self.garmin.get_activity_details(activity_id)
            return details

        except Exception as e:
            print(f"Error fetching activity details: {e}")
            self._last_error = str(e)
            return None

    def extract_hr_time_series(self, activity_id: int) -> List[Dict]:
        """
        Extract HR time series data from activity details.

        Args:
            activity_id: Garmin activity ID

        Returns:
            List of dictionaries with timestamp and hr values
        """
        try:
            details = self.get_activity_details(activity_id)
            if not details:
                return []

            # Find metric indices
            hr_index = None
            timestamp_index = None
            for descriptor in details.get("metricDescriptors", []):
                if descriptor.get("key") == "directHeartRate":
                    hr_index = descriptor.get("metricsIndex")
                elif descriptor.get("key") == "directTimestamp":
                    timestamp_index = descriptor.get("metricsIndex")

            if hr_index is None or timestamp_index is None:
                print("   HR or timestamp metrics not found in activity details")
                return []

            # Extract HR data
            hr_data = []
            for metric_entry in details.get("activityDetailMetrics", []):
                metrics = metric_entry.get("metrics", [])
                if len(metrics) > max(hr_index, timestamp_index):
                    hr = metrics[hr_index]
                    timestamp_ms = metrics[timestamp_index]

                    if hr is not None and timestamp_ms is not None:
                        from datetime import datetime, timezone

                        timestamp = datetime.fromtimestamp(
                            timestamp_ms / 1000, tz=timezone.utc
                        )
                        hr_data.append({"timestamp": timestamp, "hr": hr})

            print(f"   Extracted {len(hr_data)} HR data points")
            return hr_data

        except Exception as e:
            print(f"Error extracting HR time series: {e}")
            self._last_error = str(e)
            return []
