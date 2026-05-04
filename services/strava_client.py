"""
Strava API client for fetching activity data.
Uses the official Strava API with OAuth2 authentication.
"""

import os
import requests
from datetime import datetime
from typing import List, Dict
from pathlib import Path


class StravaClient:
    """Strava API client."""

    def __init__(self):
        self.client_id = os.getenv("STRAVA_CLIENT_ID")
        self.client_secret = os.getenv("STRAVA_CLIENT_SECRET")
        self.refresh_token = os.getenv("STRAVA_REFRESH_TOKEN")
        self.access_token = os.getenv("STRAVA_ACCESS_TOKEN")  # Direct access token
        self.base_url = "https://www.strava.com/api/v3"
        self._last_error = None
        self._env_path = Path(__file__).parent.parent / ".env"

    def _save_access_token(self, new_token: str):
        """Save new access token to .env file."""
        try:
            with open(self._env_path, "r") as f:
                lines = f.readlines()

            with open(self._env_path, "w") as f:
                for line in lines:
                    if line.startswith("STRAVA_ACCESS_TOKEN="):
                        f.write(f"STRAVA_ACCESS_TOKEN={new_token}\n")
                    else:
                        f.write(line)
            print("   New access token saved to .env")
        except Exception as e:
            print(f"   Failed to save token to .env: {e}")

    def authenticate(self):
        """Check if we have a valid access token."""
        if self.access_token:
            print("Using provided access token")
            return True

        # Fallback to refresh token method
        if not all([self.client_id, self.client_secret, self.refresh_token]):
            print("Missing Strava credentials in .env")
            return False

        try:
            response = requests.post(
                "https://www.strava.com/oauth/token",
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "refresh_token": self.refresh_token,
                    "grant_type": "refresh_token",
                },
            )

            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data["access_token"]
                print("Authenticated with Strava API")
                return True
            else:
                print(f"Strava auth failed: {response.status_code}")
                return False

        except Exception as e:
            print(f"Strava auth error: {e}")
            return False

    def get_latest_activity(self) -> Dict:
        """Get only the most recent activity."""
        if not self.access_token:
            if not self.authenticate():
                return None

        try:
            print("   Fetching most recent activity")
            response = requests.get(
                f"{self.base_url}/athlete/activities",
                headers={"Authorization": f"Bearer {self.access_token}"},
                params={"per_page": 1},
            )

            if response.status_code != 200:
                self._last_error = response.status_code
                print(f"Failed to fetch activity: {response.status_code}")
                if response.status_code == 401:
                    print("   Access token expired or invalid - attempting refresh")
                    # Try to refresh the token
                    if self.refresh_token and self.client_id and self.client_secret:
                        try:
                            refresh_response = requests.post(
                                "https://www.strava.com/oauth/token",
                                data={
                                    "client_id": self.client_id,
                                    "client_secret": self.client_secret,
                                    "refresh_token": self.refresh_token,
                                    "grant_type": "refresh_token",
                                },
                            )
                            if refresh_response.status_code == 200:
                                token_data = refresh_response.json()
                                self.access_token = token_data["access_token"]
                                self._save_access_token(self.access_token)
                                print("   Token refreshed successfully")
                                # Retry the request with new token
                                response = requests.get(
                                    f"{self.base_url}/athlete/activities",
                                    headers={
                                        "Authorization": f"Bearer {self.access_token}"
                                    },
                                    params={"per_page": 1},
                                )
                            else:
                                print(
                                    f"   Token refresh failed: {refresh_response.status_code}"
                                )
                        except Exception as e:
                            print(f"   Token refresh error: {e}")
                    else:
                        print("   No refresh token available")

                if response.status_code != 200:
                    return None

            activities = response.json()
            if not activities:
                print("   No activities found")
                return None

            activity = activities[0]
            formatted = {
                "id": str(activity["id"]),
                "type": activity["type"].lower(),
                "start_time": activity["start_date"],
                "duration_minutes": activity["elapsed_time"] / 60,
                "distance_km": activity.get("distance", 0) / 1000,
                "avg_hr": activity.get("average_heartrate"),
                "max_hr": activity.get("max_heartrate"),
                "calories": activity.get("calories"),
                "description": activity.get("description", ""),
                "title": activity.get("name", ""),
                "raw_stats": f"{activity.get('distance', 0) / 1000:.2f}km in {activity['elapsed_time'] / 60:.1f}min",
            }

            print(f"Found: {formatted['type']} - {formatted['title']}")
            return formatted

        except Exception as e:
            print(f"Error fetching latest activity: {e}")
            return None

    def get_activities_since(self, since: datetime) -> List[Dict]:
        """Get activities since a specific date."""
        if not self.access_token:
            if not self.authenticate():
                return []

        try:
            # Get activities from after the 'since' date
            after_date = int(since.timestamp())
            print(
                f"   Fetching activities after timestamp: {after_date} ({since.isoformat()})"
            )

            response = requests.get(
                f"{self.base_url}/athlete/activities",
                headers={"Authorization": f"Bearer {self.access_token}"},
                params={"after": after_date, "per_page": 100},
            )

            if response.status_code != 200:
                self._last_error = response.status_code
                print(f"Failed to fetch activities: {response.status_code}")
                if response.status_code == 401:
                    print("   Access token expired or invalid - attempting refresh")
                    # Try to refresh the token
                    if self.refresh_token and self.client_id and self.client_secret:
                        try:
                            refresh_response = requests.post(
                                "https://www.strava.com/oauth/token",
                                data={
                                    "client_id": self.client_id,
                                    "client_secret": self.client_secret,
                                    "refresh_token": self.refresh_token,
                                    "grant_type": "refresh_token",
                                },
                            )
                            if refresh_response.status_code == 200:
                                token_data = refresh_response.json()
                                self.access_token = token_data["access_token"]
                                self._save_access_token(self.access_token)
                                print("   Token refreshed successfully")
                                # Retry the request with new token
                                response = requests.get(
                                    f"{self.base_url}/athlete/activities",
                                    headers={
                                        "Authorization": f"Bearer {self.access_token}"
                                    },
                                    params={"after": after_date, "per_page": 100},
                                )
                            else:
                                print(
                                    f"   ❌ Token refresh failed: {refresh_response.status_code}"
                                )
                        except Exception as e:
                            print(f"   ❌ Token refresh error: {e}")
                    else:
                        print("   ❌ No refresh token available")
                elif response.status_code == 403:
                    print("   🚫 Insufficient permissions - check API scope")

                if response.status_code != 200:
                    return []

            activities = response.json()
            print(f"   📊 Strava returned {len(activities)} activities")
            formatted_activities = []

            for activity in activities:
                # Convert to our standard format
                formatted = {
                    "id": str(activity["id"]),
                    "type": activity["type"].lower(),
                    "start_time": activity["start_date"],
                    "duration_minutes": activity["elapsed_time"] / 60,
                    "distance_km": activity.get("distance", 0) / 1000,
                    "avg_hr": activity.get("average_heartrate"),
                    "max_hr": activity.get("max_heartrate"),
                    "calories": activity.get("calories"),
                    "description": activity.get("description", ""),
                    "title": activity.get("name", ""),
                    "raw_stats": f"{activity.get('distance', 0) / 1000:.2f}km in {activity['elapsed_time'] / 60:.1f}min",
                }

                formatted_activities.append(formatted)
                print(f"Found: {formatted['type']} - {formatted['title']}")

            return formatted_activities

        except Exception as e:
            print(f"Error fetching Strava activities: {e}")
            return []

    def setup_instructions(self):
        """Print setup instructions for Strava API."""
        print("""
🚴‍♂️ Strava API Setup Instructions:

1. Create a Strava App:
   - Go to https://www.strava.com/settings/api
   - Create a new app
   - Set callback URL: https://localhost
   - Note your Client ID and Client Secret

2. Get Authorization Code:
   - Visit: https://www.strava.com/oauth/authorize?client_id=YOUR_CLIENT_ID&response_type=code&redirect_uri=https://localhost&scope=activity:read_all
   - Replace YOUR_CLIENT_ID with your actual client ID
   - Authorize the app
   - Copy the 'code' from the redirected URL

3. Get Refresh Token:
   - Make a POST request to:
     https://www.strava.com/oauth/token
   - With data:
     client_id=YOUR_CLIENT_ID
     client_secret=YOUR_CLIENT_SECRET
     code=CODE_FROM_STEP_2
     grant_type=authorization_code

4. Update your .env file:
   STRAVA_CLIENT_ID=your_client_id
   STRAVA_CLIENT_SECRET=your_client_secret
   STRAVA_REFRESH_TOKEN=your_refresh_token

5. Test with: python test_strava.py

Alternative: Use ngrok for local testing:
   - Install ngrok: https://ngrok.com/download
   - Run: ngrok http 80
   - Use the ngrok URL as your callback URL
        """)
