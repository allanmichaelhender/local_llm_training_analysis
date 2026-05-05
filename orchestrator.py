#!/usr/bin/env python3
"""
Basic Garmin Activity Monitor
Polls Garmin every 5 minutes for new workouts, stores data, sends WhatsApp prompt, stores response.
"""

import os
import time
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

from services.database import (
    init_db,
    get_last_checked,
    set_last_checked,
    is_activity_processed,
    store_activity,
    update_user_feedback,
    get_pending_feedback_activity,
)
from services.garmin_client import GarminClient
from services.whatsapp_service import WhatsAppService


load_dotenv()

POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "300"))


def main():
    init_db()

    garmin = GarminClient()
    whatsapp = WhatsAppService()

    # Track when we sent the last prompt to filter messages
    last_prompt_time = None

    print("Garmin Activity Monitor started")
    print(f"   Polling every {POLL_INTERVAL} seconds (5 minutes)")
    print("   Press Ctrl+C to stop\n")

    try:
        while True:
            cycle_start = datetime.now()

            # Step 1: Check for new Garmin activities
            last_checked = get_last_checked()
            print(f"[{cycle_start.strftime('%H:%M:%S')}] Checking since {last_checked}")

            try:
                activities = garmin.get_activities(limit=10)
                if not activities:
                    activities = []

                for activity in activities:
                    activity_id = str(activity.get("activityId", ""))
                    if is_activity_processed(activity_id):
                        continue

                    activity_type = activity.get("activityType", {}).get(
                        "typeKey", "unknown"
                    )
                    duration = activity.get("duration", 0) / 60
                    print(f"   New activity: {activity_type} ({duration:.1f} min)")

                    # Extract HR time series from Garmin
                    hr_time_series = garmin.extract_hr_time_series(int(activity_id))

                    if hr_time_series:
                        print(f"   HR data available: {len(hr_time_series)} samples")
                        activity["hr_time_series"] = hr_time_series
                        activity["has_hr_data"] = True
                    else:
                        print("   No HR data available")
                        activity["hr_time_series"] = []
                        activity["has_hr_data"] = False

                    # Store activity with raw data
                    modality = activity.get("activityType", {}).get(
                        "typeKey", "unknown"
                    )
                    store_activity(activity_id, activity, modality)
                    print("   Activity stored in database")

                    # Send WhatsApp prompt
                    whatsapp.send_activity_prompt(activity)
                    last_prompt_time = datetime.now(timezone.utc)
                    print("   WhatsApp prompt sent")

                # Step 2: Check for user replies
                pending_id, pending_data = get_pending_feedback_activity()
                if pending_id and last_prompt_time:
                    messages = whatsapp.get_unread_messages()
                    print(f"   Checking {len(messages)} messages for feedback...")
                    for msg in messages:
                        # Only process inbound messages sent after the prompt
                        if msg.get("direction") != "inbound":
                            continue

                        msg_time = msg["date_sent"]
                        # Add 5 second buffer to account for clock skew/API delays
                        if msg_time <= last_prompt_time - timedelta(seconds=5):
                            continue

                        feedback = msg["body"].strip()
                        if feedback:
                            update_user_feedback(pending_id, feedback)
                            print(f"   Feedback received: {feedback[:50]}...")
                            print("   Feedback stored in database")

                            # Reset prompt time to prevent reprocessing
                            last_prompt_time = None
                            break  # Only process one feedback per cycle

                # Only update timestamp if we found and processed activities
                if activities:
                    set_last_checked(cycle_start)

            except Exception as e:
                print(f"   Error: {e}")
                import traceback

                traceback.print_exc()

            time.sleep(POLL_INTERVAL)

    except KeyboardInterrupt:
        print("\nShutting down...")


if __name__ == "__main__":
    main()
