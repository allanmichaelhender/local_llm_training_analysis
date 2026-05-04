"""
Sync Strava activities with local FIT files.
Matches Strava activities to FIT files by start time for detailed HR data.
"""

import os
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional

from .fit_processor import FITProcessor


class StravaFITSync:
    """Sync Strava activities with local FIT files by start time."""

    def __init__(self):
        self.fit_processor = FITProcessor()

    def find_fit_file_for_activity(self, strava_activity: Dict) -> Optional[str]:
        """
        Find FIT file that matches a Strava activity by start time.

        Args:
            strava_activity: Activity data from Strava API

        Returns:
            Path to matching FIT file or None if not found
        """
        if not self.fit_processor.is_device_connected():
            return None

        # Get Strava start time
        strava_start = strava_activity.get("start_time")
        if not strava_start:
            return None

        # Convert to datetime if it's a string
        if isinstance(strava_start, str):
            strava_start = datetime.fromisoformat(strava_start.replace("Z", "+00:00"))

        # Search for FIT files within 5 minutes of Strava start time
        tolerance = timedelta(minutes=5)
        fit_files = self._find_fit_files_in_time_range(
            strava_start - tolerance, strava_start + tolerance
        )

        if not fit_files:
            return None

        # Return the closest match
        return self._find_closest_fit_file(strava_start, fit_files)

    def _find_fit_files_in_time_range(
        self, start_time: datetime, end_time: datetime
    ) -> list:
        """Find FIT files modified within the given time range."""
        if not self.fit_processor.is_device_connected():
            return []

        fit_files = []
        activity_path = self.fit_processor.activity_path

        for filepath in os.listdir(activity_path):
            if not filepath.endswith(".fit"):
                continue

            full_path = os.path.join(activity_path, filepath)
            file_mtime = datetime.fromtimestamp(os.path.getmtime(full_path)).replace(
                tzinfo=timezone.utc
            )

            if start_time <= file_mtime <= end_time:
                # Parse the FIT file to get actual start time
                try:
                    fit_data = self.fit_processor.parse_file(full_path)
                    if fit_data and fit_data.get("start_time"):
                        fit_start = fit_data["start_time"]
                        if isinstance(fit_start, str):
                            fit_start = datetime.fromisoformat(
                                fit_start.replace("Z", "+00:00")
                            )

                        if start_time <= fit_start <= end_time:
                            fit_files.append((full_path, fit_start))
                except Exception:
                    # If we can't parse the file, use file mtime as fallback
                    fit_files.append((full_path, file_mtime))

        return fit_files

    def _find_closest_fit_file(
        self, target_time: datetime, fit_files: list
    ) -> Optional[str]:
        """Find FIT file with start time closest to target time."""
        if not fit_files:
            return None

        # Sort by time difference
        fit_files.sort(key=lambda x: abs(x[1] - target_time))
        return fit_files[0][0]

    def sync_activity_with_fit_data(self, strava_activity: Dict) -> Dict:
        """
        Enhance Strava activity with FIT file HR data.

        Args:
            strava_activity: Activity data from Strava API

        Returns:
            Enhanced activity data with HR time series
        """
        fit_file = self.find_fit_file_for_activity(strava_activity)

        if not fit_file:
            return strava_activity

        # Extract HR data from FIT file
        from .hr_aggregator import HRAggregator

        hr_agg = HRAggregator()
        hr_series = hr_agg.extract_hr_averages(fit_file)

        # Get FIT file sport type for more accurate modality
        fit_data = self.fit_processor.parse_file(fit_file)
        fit_sport = fit_data.get("type", "unknown") if fit_data else "unknown"

        # Calculate HR zones
        from .hr_zones import HRZones

        hr_zones = HRZones()
        zone_distribution = hr_zones.calculate_zone_distribution(hr_series, fit_sport)
        zone_summary = hr_zones.get_zone_summary(hr_series, fit_sport)
        dominant_zone = hr_zones.get_dominant_zone(hr_series, fit_sport)

        # Add FIT data to Strava activity
        enhanced = strava_activity.copy()
        enhanced.update(
            {
                "fit_file_path": fit_file,
                "hr_time_series": hr_series,
                "has_hr_data": True,
                "fit_sport": fit_sport,  # Store Garmin sport type
                "hr_zones": zone_distribution,
                "hr_zone_summary": zone_summary,
                "dominant_hr_zone": dominant_zone,
            }
        )

        return enhanced

    def batch_sync_activities(self, strava_activities: list) -> list:
        """
        Sync multiple Strava activities with FIT files.

        Args:
            strava_activities: List of Strava activity dictionaries

        Returns:
            List of enhanced activities with FIT data where available
        """
        enhanced_activities = []

        for activity in strava_activities:
            enhanced = self.sync_activity_with_fit_data(activity)
            enhanced_activities.append(enhanced)

        return enhanced_activities
