"""
Garmin Connect MCP client for fetching activity data.
Wraps Garmin Connect MCP tools for activity detection and HR data retrieval.
"""

from typing import List, Dict, Optional


class GarminClient:
    """Garmin Connect MCP client."""

    def __init__(self):
        """Initialize Garmin client (MCP tools are called via Cascade)."""
        self._last_error = None

    def get_activities(self, limit: int = 20) -> List[Dict]:
        """
        Get recent activities from Garmin Connect MCP.

        Args:
            limit: Number of activities to return (1-100, default 20)

        Returns:
            List of complete raw activity dictionaries from MCP
        """
        try:
            print(f"   Fetching {limit} most recent Garmin activities")

            # Call MCP tool directly
            activities = mcp0_get_activities(limit=limit)

            if not activities:
                print("   No Garmin activities found")
                return []

            # Return raw activities without formatting
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
            details = mcp0_get_activity_details(activityId=activity_id)
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
