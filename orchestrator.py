#!/usr/bin/env python3
"""
Minimalist Garmin AI Coach
Polls for new activities, requests feedback via WhatsApp, generates LLM summary.
"""

import os
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv

from services.database import (
    init_db,
    get_last_checked,
    set_last_checked,
    is_activity_processed,
    store_activity,
    update_user_feedback,
    update_llm_summary,
    get_pending_feedback_activity,
)
from services.strava_client import StravaClient
from services.strava_fit_sync import StravaFITSync
from services.whatsapp_service import WhatsAppService
from services.llm_service import LLMService


load_dotenv()

POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "120"))
USE_BROWSER = os.getenv("USE_BROWSER", "true").lower() == "true"


def main():
    init_db()

    garmin = StravaClient()
    sync_service = StravaFITSync()
    whatsapp = WhatsAppService()
    llm = LLMService()

    # Track when we sent the last prompt to filter messages
    last_prompt_time = None

    print("Garmin AI Coach started")
    print(f"   Polling every {POLL_INTERVAL} seconds")
    print("   Press Ctrl+C to stop\n")

    try:
        while True:
            cycle_start = datetime.now()

            # Step 1: Check for new Garmin activities
            last_checked = get_last_checked()
            print(f"[{cycle_start.strftime('%H:%M:%S')}] Checking since {last_checked}")

            try:
                activity = garmin.get_latest_activity()
                activities = [activity] if activity else []

                # Sync with FIT files for HR data
                enhanced_activities = sync_service.batch_sync_activities(activities)

                for activity in enhanced_activities:
                    if is_activity_processed(activity["id"]):
                        continue

                    print(
                        f"   New activity: {activity['type']} ({activity['duration_minutes']:.1f} min)"
                    )
                    if activity.get("has_hr_data"):
                        print("   HR data available from FIT file")

                    modality = activity.get(
                        "fit_sport", activity.get("type", "unknown")
                    )
                    store_activity(activity["id"], activity, modality)
                    whatsapp.send_activity_prompt(activity)
                    from datetime import timezone

                    last_prompt_time = datetime.now(timezone.utc)
                    print("   WhatsApp prompt sent")

                # Step 2: Check for user replies
                pending_id, pending_data = get_pending_feedback_activity()
                if pending_id and last_prompt_time:
                    messages = whatsapp.get_unread_messages()
                    print(f"   Checking {len(messages)} messages for feedback...")
                    for msg in messages:
                        print(
                            f"   Message: SID={msg['sid'][:10]}..., Direction={msg.get('direction')}, Time={msg['date_sent']}, Body={msg['body'][:30] if msg['body'] else 'None'}..."
                        )

                        # Only process inbound messages sent after the prompt
                        if msg.get("direction") != "inbound":
                            print(f"   REJECTED: Not inbound")
                            continue

                        # Convert message date to datetime for comparison
                        # Both should be timezone-aware now
                        msg_time = msg["date_sent"]
                        # Add 5 second buffer to account for clock skew/API delays
                        if msg_time <= last_prompt_time - timedelta(seconds=5):
                            print(
                                f"   REJECTED: Message time {msg_time} <= prompt time {last_prompt_time} (with buffer)"
                            )
                            continue

                        print(f"   ACCEPTED: Message qualifies as feedback")
                        # Simple logic: if we have a pending activity and new message, use it
                        feedback = msg["body"].strip()
                        if feedback:
                            update_user_feedback(pending_id, feedback)
                            print(f"   Feedback received: {feedback[:50]}...")

                            # Use HR time series from synced activity data
                            hr_series = pending_data.get("hr_time_series", [])

                            # Generate and send summary with HR data
                            print(
                                f"   Generating LLM summary for activity {pending_id}..."
                            )
                            summary = llm.generate_summary(
                                pending_data, feedback, hr_series
                            )
                            update_llm_summary(pending_id, summary)
                            whatsapp.send_summary(summary)
                            print("   Summary sent")

                            # Reset prompt time to prevent reprocessing
                            last_prompt_time = None
                            break  # Only process one feedback per cycle

                # Only update timestamp if we found and processed activities
                if activities:
                    set_last_checked(cycle_start)

            except Exception as e:
                print(f"   Error: {e}")

            time.sleep(POLL_INTERVAL)

    except KeyboardInterrupt:
        print("\nShutting down...")


if __name__ == "__main__":
    main()
