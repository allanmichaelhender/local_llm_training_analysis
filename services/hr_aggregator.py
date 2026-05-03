"""
Heart rate data aggregation service.
Extracts HR data from FIT files and creates 10-second averages.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from fitparse import FitFile


class HRAggregator:
    """Aggregate heart rate data into time buckets."""

    def __init__(self, bucket_seconds: int = 10):
        """
        Initialize HR aggregator.

        Args:
            bucket_seconds: Size of time buckets (default: 10 seconds)
        """
        self.bucket_seconds = bucket_seconds

    def extract_hr_averages(self, filepath: str) -> List[Dict]:
        """
        Extract HR data from FIT file and create time-bucketed averages.

        Args:
            filepath: Path to FIT file

        Returns:
            List of dictionaries with timestamp and avg_hr for each bucket
        """
        fitfile = FitFile(filepath)
        hr_data = []

        # Collect all HR records
        for record in fitfile.get_messages("record"):
            timestamp = record.get_value("timestamp")
            hr = record.get_value("heart_rate")
            if timestamp and hr:
                hr_data.append((timestamp, hr))

        if not hr_data:
            return []

        # Sort by timestamp
        hr_data.sort(key=lambda x: x[0])

        # Create time buckets
        buckets = self._create_time_buckets(hr_data)

        return buckets

    def _create_time_buckets(self, hr_data: List[Tuple[datetime, int]]) -> List[Dict]:
        """Create time-bucketed HR averages."""
        if not hr_data:
            return []

        buckets = []
        current_bucket = []
        bucket_start = hr_data[0][0]

        for timestamp, hr in hr_data:
            # Calculate which bucket this belongs to
            seconds_diff = (timestamp - bucket_start).total_seconds()
            bucket_num = int(seconds_diff // self.bucket_seconds)

            # If we've moved to a new bucket, process the previous one
            if bucket_num > len(buckets):
                if current_bucket:
                    avg_hr = sum(hr for _, hr in current_bucket) / len(current_bucket)
                    buckets.append(
                        {
                            "timestamp": bucket_start
                            + timedelta(seconds=len(buckets) * self.bucket_seconds),
                            "avg_hr": round(avg_hr, 1),
                            "sample_count": len(current_bucket),
                        }
                    )
                    current_bucket = []

            current_bucket.append((timestamp, hr))

        # Process the last bucket
        if current_bucket:
            avg_hr = sum(hr for _, hr in current_bucket) / len(current_bucket)
            buckets.append(
                {
                    "timestamp": bucket_start
                    + timedelta(seconds=len(buckets) * self.bucket_seconds),
                    "avg_hr": round(avg_hr, 1),
                    "sample_count": len(current_bucket),
                }
            )

        return buckets

    def get_hr_summary_stats(self, filepath: str) -> Dict:
        """Get summary HR statistics from FIT file."""
        fitfile = FitFile(filepath)
        hr_values = []

        for record in fitfile.get_messages("record"):
            hr = record.get_value("heart_rate")
            if hr:
                hr_values.append(hr)

        if not hr_values:
            return {}

        return {
            "min_hr": min(hr_values),
            "max_hr": max(hr_values),
            "avg_hr": sum(hr_values) / len(hr_values),
            "sample_count": len(hr_values),
            "duration_seconds": len(hr_values),  # Assuming 1-second samples
        }
