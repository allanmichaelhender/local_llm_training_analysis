#!/usr/bin/env python3
"""View and query activities database."""

import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.database import init_db


def view_activities(limit=10, modality=None):
    """View recent activities from database."""
    import sqlite3

    DB_PATH = os.path.join(os.path.dirname(__file__), "data", "activities.db")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if modality:
        cursor.execute(
            """
            SELECT id, modality, activity_data, user_feedback, llm_summary, created_at, processed_at
            FROM activities 
            WHERE modality = ?
            ORDER BY created_at DESC 
            LIMIT ?
        """,
            (modality, limit),
        )
    else:
        cursor.execute(
            """
            SELECT id, modality, activity_data, user_feedback, llm_summary, created_at, processed_at
            FROM activities 
            ORDER BY created_at DESC 
            LIMIT ?
        """,
            (limit,),
        )

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("No activities found.")
        return

    print("\n" + "=" * 80)
    print("Showing " + str(len(rows)) + " most recent activities")
    print("=" * 80 + "\n")

    for row in rows:
        (
            activity_id,
            modality,
            activity_data,
            user_feedback,
            llm_summary,
            created_at,
            processed_at,
        ) = row

        # Parse activity data
        try:
            activity = json.loads(activity_data)
        except json.JSONDecodeError:
            activity = {}

        print(f"🆔 ID: {activity_id}")
        print(f"🏃 Type: {modality}")
        print(f"📅 Created: {created_at}")
        if processed_at:
            print(f"✅ Processed: {processed_at}")

        # Basic activity info
        print(f"⏱️  Duration: {activity.get('duration_minutes', 'N/A'):.1f} min")
        print(f"📏 Distance: {activity.get('distance_km', 'N/A'):.2f} km")
        print(f"💓 Avg HR: {activity.get('avg_hr', 'N/A')} bpm")
        print(f"🔥 Max HR: {activity.get('max_hr', 'N/A')} bpm")
        print(f"🔥 Calories: {activity.get('calories', 'N/A')}")

        # HR zones if available
        if activity.get("hr_zone_summary"):
            print(f"\n📊 HR Zones:")
            print(activity["hr_zone_summary"])

        # User feedback
        if user_feedback:
            print(f"\n💬 User Feedback:")
            print(f"   {user_feedback}")

        # LLM summary
        if llm_summary:
            print("\n AI Summary:")
            print("   " + llm_summary)

        print("\n" + "-" * 60 + "\n")


def view_activity_details(activity_id):
    """View full details for a specific activity."""
    import sqlite3

    DB_PATH = os.path.join(os.path.dirname(__file__), "data", "activities.db")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, modality, activity_data, user_feedback, llm_summary, created_at, processed_at
        FROM activities 
        WHERE id = ?
    """,
        (activity_id,),
    )

    row = cursor.fetchone()
    conn.close()

    if not row:
        print(f"Activity {activity_id} not found.")
        return

    (
        activity_id,
        modality,
        activity_data,
        user_feedback,
        llm_summary,
        created_at,
        processed_at,
    ) = row

    print(f"\n{'=' * 80}")
    print(f"Activity Details: {activity_id}")
    print(f"{'=' * 80}\n")

    # Parse and display full activity data
    activity = json.loads(activity_data)

    print("📋 ACTIVITY DATA:")
    print(json.dumps(activity, indent=2, default=str))

    if user_feedback:
        print(f"\n💬 USER FEEDBACK:")
        print(user_feedback)

    if llm_summary:
        print(f"\n🤖 AI SUMMARY:")
        print(llm_summary)


def list_modalities():
    """List all activity types in database."""
    import sqlite3

    DB_PATH = os.path.join(os.path.dirname(__file__), "data", "activities.db")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT modality, COUNT(*) as count
        FROM activities 
        GROUP BY modality 
        ORDER BY count DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    print(f"\n{'=' * 50}")
    print("Activity Types Summary")
    print(f"{'=' * 50}\n")

    for modality, count in rows:
        print(f"{modality:15} : {count:3} activities")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="View activities database")
    parser.add_argument(
        "--limit", type=int, default=10, help="Number of recent activities to show"
    )
    parser.add_argument("--modality", type=str, help="Filter by activity type")
    parser.add_argument("--id", type=str, help="Show details for specific activity ID")
    parser.add_argument(
        "--types", action="store_true", help="Show summary of activity types"
    )

    args = parser.parse_args()

    # Initialize database if needed
    init_db()

    if args.id:
        view_activity_details(args.id)
    elif args.types:
        list_modalities()
    else:
        view_activities(limit=args.limit, modality=args.modality)


if __name__ == "__main__":
    main()
