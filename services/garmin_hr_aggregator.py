"""
Heart rate data service for Garmin Connect MCP.
Extracts HR data from Garmin activity details without aggregation.
"""

from typing import List, Dict


class GarminHRAggregator:
    """Process heart rate data from Garmin Connect MCP."""

    def process_hr_data(self, hr_time_series: List[Dict]) -> List[Dict]:
        """
        Process HR time series data (pass through without aggregation).

        Args:
            hr_time_series: List of dictionaries with 'timestamp' and 'hr' keys

        Returns:
            Same HR time series data, sorted by timestamp
        """
        if not hr_time_series:
            return []

        # Sort by timestamp and return as-is
        hr_data = sorted(hr_time_series, key=lambda x: x["timestamp"])
        return hr_data

    def get_hr_summary_stats(self, hr_time_series: List[Dict]) -> Dict:
        """Get summary HR statistics from time series data."""
        if not hr_time_series:
            return {}

        hr_values = [entry["hr"] for entry in hr_time_series if entry["hr"] is not None]

        if not hr_values:
            return {}

        return {
            "min_hr": min(hr_values),
            "max_hr": max(hr_values),
            "avg_hr": sum(hr_values) / len(hr_values),
            "sample_count": len(hr_values),
        }
