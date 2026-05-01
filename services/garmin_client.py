import os
from datetime import datetime, timedelta
from typing import List, Dict
from garminconnect import Garmin


class GarminClient:
    def __init__(self):
        self.email = os.getenv("GARMIN_EMAIL")
        self.password = os.getenv("GARMIN_PASSWORD")
        self.client = None

    def connect(self):
        if not self.client:
            self.client = Garmin(self.email, self.password)
            self.client.login()
        return self.client

    def get_activities_since(self, since: datetime) -> List[Dict]:
        client = self.connect()

        # Get activities from last 10 days to be safe
        start_date = since - timedelta(days=10)

        try:
            activities = client.get_activities_by_date(
                start_date.strftime("%Y-%m-%d"), datetime.now().strftime("%Y-%m-%d")
            )
        except Exception as e:
            print(f"Error fetching activities: {e}")
            return []

        new_activities = []
        for activity in activities:
            activity_time = datetime.fromisoformat(
                activity["startTimeLocal"].replace("Z", "+00:00").replace("+00:00", "")
            )
            if activity_time > since:
                new_activities.append(self._format_activity(activity))

        return new_activities

    def _format_activity(self, activity: Dict) -> Dict:
        return {
            "id": str(activity["activityId"]),
            "type": activity.get("activityType", {}).get("typeKey", "unknown"),
            "start_time": activity["startTimeLocal"],
            "duration_minutes": activity.get("duration", 0) / 60,
            "distance_km": activity.get("distance", 0) / 1000,
            "avg_hr": activity.get("averageHR"),
            "max_hr": activity.get("maxHR"),
            "calories": activity.get("calories"),
            "description": activity.get("description", ""),
        }
