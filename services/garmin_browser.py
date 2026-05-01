"""
Browser-based Garmin Connect scraper using Playwright.
Uses saved cookies/session so you only need to log in once via browser.
"""

import pickle
from datetime import datetime
from pathlib import Path
from typing import List, Dict
from playwright.sync_api import sync_playwright

COOKIES_PATH = Path(__file__).parent.parent / "data" / "garmin_cookies.pkl"


class GarminBrowserClient:
    """Scrapes Garmin Connect via browser using saved session."""

    def __init__(self, headless: bool = True):
        self.headless = headless
        self.base_url = "https://connect.garmin.com"

    def _save_cookies(self, context):
        COOKIES_PATH.parent.mkdir(exist_ok=True)
        cookies = context.cookies()
        with open(COOKIES_PATH, "wb") as f:
            pickle.dump(cookies, f)

    def _load_cookies(self, context):
        if COOKIES_PATH.exists():
            with open(COOKIES_PATH, "rb") as f:
                cookies = pickle.load(f)
                context.add_cookies(cookies)
                return True
        return False

    def get_activities_since(self, since: datetime) -> List[Dict]:
        """Fetch activities from Garmin Connect web interface."""

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            context = browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            )

            # Try to load existing cookies
            has_cookies = self._load_cookies(context)
            page = context.new_page()

            # Navigate to activities page
            activities_url = f"{self.base_url}/modern/activities"
            page.goto(activities_url, wait_until="networkidle")

            # Check if we're logged in (look for login form or activities list)
            if page.locator("input#username").is_visible() or "signin" in page.url:
                if has_cookies:
                    print("   Cookies expired, need fresh login")

                print("   🔐 Please log in to Garmin Connect in the browser...")
                print(f"   URL: {page.url}")
                input("   Press ENTER after you've logged in...")

                # Save the new cookies
                self._save_cookies(context)
                print("   ✓ Session saved for future runs")

            # Now scrape activities
            print("   📊 Fetching activities...")

            # Wait for activity list to load
            page.wait_for_selector(".list-item-container", timeout=10000)

            activities = []
            activity_cards = page.locator(".list-item-container").all()

            for card in activity_cards[:20]:  # Check last 20 activities
                try:
                    # Extract activity details
                    title_elem = card.locator(".activity-name").first
                    title = (
                        title_elem.inner_text()
                        if title_elem.is_visible()
                        else "Unknown"
                    )

                    time_elem = card.locator("time").first
                    time_text = (
                        time_elem.get_attribute("datetime") if time_elem else None
                    )

                    if time_text:
                        activity_time = datetime.fromisoformat(
                            time_text.replace("Z", "+00:00").replace("+00:00", "")
                        )
                    else:
                        continue

                    # Only include activities after our 'since' timestamp
                    if activity_time <= since:
                        continue

                    # Get activity type from icon/class
                    type_elem = card.locator(".activity-icon").first
                    activity_type = "unknown"
                    if type_elem:
                        class_list = type_elem.get_attribute("class") or ""
                        if "running" in class_list:
                            activity_type = "running"
                        elif "cycling" in class_list:
                            activity_type = "cycling"
                        elif "swimming" in class_list:
                            activity_type = "swimming"
                        elif "strength" in class_list:
                            activity_type = "strength_training"

                    # Get activity ID from link
                    link_elem = card.locator("a[href*='activity']").first
                    href = link_elem.get_attribute("href") if link_elem else ""
                    activity_id = (
                        href.split("/")[-1]
                        if "/" in href
                        else str(int(activity_time.timestamp()))
                    )

                    # Get stats if available
                    stats = (
                        card.locator(".stats").inner_text()
                        if card.locator(".stats").first.is_visible()
                        else ""
                    )

                    activity = {
                        "id": activity_id,
                        "type": activity_type,
                        "start_time": activity_time.isoformat(),
                        "title": title,
                        "raw_stats": stats,
                        "duration_minutes": 0,  # Would need to parse from stats
                        "distance_km": 0,
                        "avg_hr": None,
                        "max_hr": None,
                        "calories": None,
                    }

                    activities.append(activity)

                except Exception as e:
                    print(f"   Warning: Could not parse activity card: {e}")
                    continue

            browser.close()
            return activities
