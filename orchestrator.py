#!/usr/bin/env python3
"""
Minimalist Garmin AI Coach
Polls for new activities, requests feedback via WhatsApp, generates LLM summary.
"""

import os
import time
from datetime import datetime
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
from services.fit_monitor import FITMonitor
from services.hr_aggregator import HRAggregator
from services.whatsapp_service import WhatsAppService
from services.llm_service import LLMService


load_dotenv()

POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "120"))
USE_BROWSER = os.getenv("USE_BROWSER", "true").lower() == "true"


def main():
    init_db()

    garmin = FITMonitor()
    hr_agg = HRAggregator()
    whatsapp = WhatsAppService()
    llm = LLMService()

    # Track WhatsApp message SIDs we've already seen
    processed_sids = set()

    print("🚀 Garmin AI Coach started")
    print(f"   Polling every {POLL_INTERVAL} seconds")
    print("   Press Ctrl+C to stop\n")

    try:
        while True:
            cycle_start = datetime.now()

            # Step 1: Check for new Garmin activities
            last_checked = get_last_checked()
            print(f"[{cycle_start.strftime('%H:%M:%S')}] Checking since {last_checked}")

            try:
                activities = garmin.check_for_new_workouts()

                for activity in activities:
                    if is_activity_processed(activity["id"]):
                        continue

                    print(
                        f"   📍 New activity: {activity['type']} ({activity['duration_minutes']:.1f} min)"
                    )
                    store_activity(activity["id"], activity)
                    whatsapp.send_activity_prompt(activity)
                    print("   📤 WhatsApp prompt sent")

                # Step 2: Check for user replies
                pending_id, pending_data = get_pending_feedback_activity()
                if pending_id:
                    messages = whatsapp.get_unread_messages()
                    for msg in messages:
                        if msg["sid"] in processed_sids:
                            continue

                        # Simple logic: if we have a pending activity and new message, use it
                        feedback = msg["body"].strip()
                        if feedback:
                            update_user_feedback(pending_id, feedback)
                            print(f"   📨 Feedback received: {feedback[:50]}...")

                            # Extract HR time series data
                            hr_series = hr_agg.extract_hr_averages(
                                pending_data.get("file_path", "")
                            )

                            # Generate and send summary with HR data
                            summary = llm.generate_summary(
                                pending_data, feedback, hr_series
                            )
                            update_llm_summary(pending_id, summary)
                            whatsapp.send_summary(summary)
                            print("   ✅ Summary sent")

                            processed_sids.add(msg["sid"])
                            break  # Only process one feedback per cycle

                set_last_checked(cycle_start)

            except Exception as e:
                print(f"   ❌ Error: {e}")

            time.sleep(POLL_INTERVAL)

    except KeyboardInterrupt:
        print("\n👋 Shutting down...")


if __name__ == "__main__":
    main()
