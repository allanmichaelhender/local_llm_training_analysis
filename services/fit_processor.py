"""
FIT file processor for parsing Garmin activity files.
Uses fitparse to extract workout data directly from .fit files.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from fitparse import FitFile


class FITProcessor:
    """Process Garmin .fit activity files."""

    def __init__(self, activity_path: Optional[str] = None):
        """
        Initialize FIT processor.

        Args:
            activity_path: Path to Garmin Activity folder. Defaults to common mount points.
        """
        self.activity_path = activity_path or self._detect_garmin_path()

    def _detect_garmin_path(self) -> Optional[str]:
        """Auto-detect Garmin device mount path."""
        common_paths = [
            # Local project directory (for manual file drops)
            os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fit_files"
            ),
            # Windows
            "D:/Garmin/Activity",
            "E:/Garmin/Activity",
            "F:/Garmin/Activity",
            "G:/Garmin/Activity",
            # macOS
            "/Volumes/GARMIN/Activity",
            "/Volumes/Garmin/Activity",
            # Linux
            "/media/GARMIN/Activity",
            "/mnt/garmin/Activity",
        ]
        for path in common_paths:
            if os.path.exists(path):
                return path
        return None

    def is_device_connected(self) -> bool:
        """Check if Garmin device is mounted."""
        return self.activity_path is not None and os.path.exists(self.activity_path)

    def find_new_files(self, since: datetime) -> List[str]:
        """Find .fit files modified after 'since' timestamp."""
        if not self.is_device_connected():
            return []

        fit_files = []

        for filepath in Path(self.activity_path).glob("*.fit"):
            mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
            if mtime > since:
                fit_files.append((filepath, mtime))

        # Sort by modification time, newest last
        fit_files.sort(key=lambda x: x[1])
        return [str(f[0]) for f in fit_files]

    def parse_file(self, filepath: str) -> Optional[Dict]:
        """Parse a single .fit file and extract activity data."""
        try:
            fitfile = FitFile(filepath)

            # Extract session data (activity summary)
            for record in fitfile.get_messages("session"):
                data = record.get_values()
                return {
                    "id": self._generate_id(filepath, data),
                    "type": data.get("sport", "unknown"),
                    "start_time": data.get("start_time"),
                    "duration_minutes": (data.get("total_elapsed_time", 0) or 0) / 60,
                    "distance_km": (data.get("total_distance", 0) or 0) / 1000,
                    "avg_hr": data.get("avg_heart_rate"),
                    "max_hr": data.get("max_heart_rate"),
                    "calories": data.get("total_calories"),
                    "title": self._generate_title(data),
                    "description": f"Imported from {os.path.basename(filepath)}",
                    "raw_stats": self._format_stats(data),
                    "source": "garmin_fit",
                    "file_path": filepath,
                }

        except Exception as e:
            print(f"Error parsing FIT file {filepath}: {e}")
            return None

    def _generate_id(self, filepath: str, data: dict) -> str:
        """Generate unique activity ID from file and timestamp."""
        start_time = data.get("start_time")
        if start_time:
            return f"fit_{start_time.strftime('%Y%m%d_%H%M%S')}"
        return f"fit_{os.path.basename(filepath)}"

    def _generate_title(self, data: dict) -> str:
        """Generate activity title from sport and time."""
        sport = data.get("sport", "Activity")
        start = data.get("start_time")
        if start:
            return f"{sport.title()} - {start.strftime('%H:%M')}"
        return f"{sport.title()} Activity"

    def _format_stats(self, data: dict) -> str:
        """Format raw stats for display."""
        distance_km = (data.get("total_distance", 0) or 0) / 1000
        duration_min = (data.get("total_elapsed_time", 0) or 0) / 60
        return f"{distance_km:.2f}km in {duration_min:.1f}min"

    def get_time_series(self, filepath: str) -> List[Dict]:
        """Extract per-second data (HR, speed, GPS) from .fit file."""
        records = []
        try:
            fitfile = FitFile(filepath)
            for record in fitfile.get_messages("record"):
                data = record.get_values()
                records.append(
                    {
                        "timestamp": data.get("timestamp"),
                        "heart_rate": data.get("heart_rate"),
                        "speed_ms": data.get("speed"),
                        "distance_m": data.get("distance"),
                        "latitude": data.get("position_lat"),
                        "longitude": data.get("position_long"),
                        "altitude": data.get("altitude"),
                        "cadence": data.get("cadence"),
                        "power": data.get("power"),
                        "temperature": data.get("temperature"),
                    }
                )
        except Exception as e:
            print(f"Error reading time series from {filepath}: {e}")

        return records

    def get_lap_data(self, filepath: str) -> List[Dict]:
        """Extract lap/split data from .fit file."""
        laps = []
        try:
            fitfile = FitFile(filepath)
            for lap in fitfile.get_messages("lap"):
                data = lap.get_values()
                laps.append(
                    {
                        "start_time": data.get("start_time"),
                        "duration_minutes": (data.get("total_elapsed_time", 0) or 0)
                        / 60,
                        "distance_km": (data.get("total_distance", 0) or 0) / 1000,
                        "avg_hr": data.get("avg_heart_rate"),
                        "max_hr": data.get("max_heart_rate"),
                        "avg_speed": data.get("avg_speed"),
                        "max_speed": data.get("max_speed"),
                        "avg_cadence": data.get("avg_cadence"),
                        "avg_power": data.get("avg_power"),
                    }
                )
        except Exception as e:
            print(f"Error reading lap data from {filepath}: {e}")

        return laps
