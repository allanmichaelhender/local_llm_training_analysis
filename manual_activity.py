#!/usr/bin/env python3
"""
Manual activity entry - bypass Garmin API entirely.
You can manually input workout data and still get WhatsApp + LLM analysis.
"""

from datetime import datetime
from dotenv import load_dotenv

from services.database import (
    init_db,
    store_activity,
    get_pending_feedback_activity,
    update_user_feedback,
    update_llm_summary,
)
from services.whatsapp_service import WhatsAppService
from services.llm_service import LLMService

load_dotenv()


def get_manual_activity():
    """Get activity details from user input."""
    print("📝 Manual Activity Entry")
    print("=" * 40)

    activity = {
        "id": f"manual_{int(datetime.now().timestamp())}",
        "type": input(
            "Activity type (running/cycling/swimming/strength/etc): "
        ).lower(),
        "duration_minutes": float(input("Duration (minutes): ")),
        "distance_km": float(input("Distance (km, 0 if none): ")),
        "avg_hr": int(input("Average heart rate (0 if none): ") or "0"),
        "max_hr": int(input("Max heart rate (0 if none): ") or "0"),
        "calories": int(input("Calories (0 if none): ") or "0"),
        "description": input("Notes/description: "),
        "start_time": datetime.now().isoformat(),
    }

    return activity


def main():
    init_db()

    whatsapp = WhatsAppService()
    llm = LLMService()

    print("🚀 Manual Activity Coach")
    print("   Enter workout data manually, get WhatsApp + LLM analysis")
    print()

    # Get activity from user
    activity = get_manual_activity()

    print(
        f"\n📍 Activity recorded: {activity['type']} ({activity['duration_minutes']:.1f} min)"
    )

    # Store activity
    store_activity(activity["id"], activity)

    # Send WhatsApp prompt
    whatsapp.send_activity_prompt(activity)
    print("📤 WhatsApp prompt sent")

    # Wait for user reply
    print("⏳ Waiting for your WhatsApp reply...")
    input("Press ENTER after you've replied on WhatsApp...")

    # Check for feedback
    pending_id, pending_data = get_pending_feedback_activity()
    if pending_id:
        # Get messages (simplified - just ask user to input their reply)
        feedback = input("Enter your WhatsApp reply (RPE + notes): ")

        if feedback:
            update_user_feedback(pending_id, feedback)
            print(f"📨 Feedback received: {feedback[:50]}...")

            # Generate and send summary
            summary = llm.generate_summary(pending_data, feedback)
            update_llm_summary(pending_id, summary)
            whatsapp.send_summary(summary)
            print("✅ Summary sent via WhatsApp")

    print("\n✨ Done! Your activity has been analyzed.")


if __name__ == "__main__":
    main()
