"""
Heart rate zone calculations for different activity types.
"""

from typing import Dict, List, Tuple


class HRZones:
    """Calculate and analyze heart rate zones."""

    def __init__(self):
        # Define base zones for running
        self.base_zones = {
            "Z1": (120, 150),
            "Z2": (150, 165),
            "Z3": (165, 180),
            "Z4": (180, 190),
            "Z5": (190, 999),  # 190+ bpm
        }

    def get_zones_for_modality(self, modality: str) -> Dict[str, Tuple[int, int]]:
        """
        Get HR zones for specific activity type.

        Args:
            modality: Activity type (running, training, cycling, etc.)

        Returns:
            Dictionary with zone ranges
        """
        if modality == "running":
            return self.base_zones.copy()
        else:
            # Subtract 10 from all zone values for non-running activities
            adjusted_zones = {}
            for zone, (min_hr, max_hr) in self.base_zones.items():
                adjusted_zones[zone] = (max(0, min_hr - 10), max(0, max_hr - 10))
            return adjusted_zones

    def calculate_zone_distribution(
        self, hr_series: List[Dict], modality: str
    ) -> Dict[str, Dict]:
        """
        Calculate time spent in each HR zone.

        Args:
            hr_series: List of HR data points with avg_hr
            modality: Activity type for zone calculation

        Returns:
            Dictionary with zone statistics
        """
        zones = self.get_zones_for_modality(modality)
        zone_stats = {}

        # Initialize zone counters
        for zone_name in zones:
            zone_stats[zone_name] = {"time_seconds": 0, "percentage": 0.0, "samples": 0}

        total_samples = 0

        # Count time in each zone
        for hr_data in hr_series:
            avg_hr = hr_data.get("avg_hr", 0)
            sample_count = hr_data.get("sample_count", 1)

            # Find which zone this HR belongs to
            for zone_name, (min_hr, max_hr) in zones.items():
                if min_hr <= avg_hr < max_hr:
                    zone_stats[zone_name]["time_seconds"] += (
                        sample_count * 10
                    )  # 10-second buckets
                    zone_stats[zone_name]["samples"] += 1
                    total_samples += 1
                    break

        # Calculate percentages
        if total_samples > 0:
            for zone_name in zone_stats:
                zone_stats[zone_name]["percentage"] = (
                    zone_stats[zone_name]["samples"] / total_samples * 100
                )

        return zone_stats

    def get_zone_summary(self, hr_series: List[Dict], modality: str) -> str:
        """
        Generate human-readable zone summary.

        Args:
            hr_series: List of HR data points
            modality: Activity type

        Returns:
            Formatted zone summary string
        """
        zones = self.get_zones_for_modality(modality)
        distribution = self.calculate_zone_distribution(hr_series, modality)

        summary = f"HR Zones ({modality}):\n"
        for zone in ["Z1", "Z2", "Z3", "Z4", "Z5"]:
            if zone in distribution:
                stats = distribution[zone]
                min_hr, max_hr = zones[zone]
                max_display = "+" if max_hr >= 999 else max_hr
                time_min = stats["time_seconds"] / 60
                summary += f"  {zone}: {min_hr}-{max_display} bpm ({stats['percentage']:.1f}%, {time_min:.1f} min)\n"

        return summary.strip()

    def get_dominant_zone(self, hr_series: List[Dict], modality: str) -> str:
        """
        Find the HR zone with most time spent.

        Args:
            hr_series: List of HR data points
            modality: Activity type

        Returns:
            Zone name with highest percentage
        """
        distribution = self.calculate_zone_distribution(hr_series, modality)

        if not distribution:
            return "Unknown"

        dominant_zone = max(distribution.items(), key=lambda x: x[1]["percentage"])
        return dominant_zone[0]
