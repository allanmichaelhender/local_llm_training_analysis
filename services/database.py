import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "activities.db"


def init_db():
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS activities (
            id TEXT PRIMARY KEY,
            activity_data TEXT,
            modality TEXT,
            user_feedback TEXT,
            llm_summary TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            processed_at TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS state (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)

    conn.commit()
    conn.close()


def get_last_checked():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM state WHERE key = 'last_checked'")
    row = cursor.fetchone()
    conn.close()

    if row:
        return datetime.fromisoformat(row[0])
    return datetime.now() - timedelta(days=30)


def set_last_checked(timestamp: datetime):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO state (key, value) VALUES (?, ?)",
        ("last_checked", timestamp.isoformat()),
    )
    conn.commit()
    conn.close()


def is_activity_processed(activity_id: str) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM activities WHERE id = ?", (activity_id,))
    row = cursor.fetchone()
    conn.close()
    return row is not None


def store_activity(activity_id: str, activity_data: dict, modality: str = "unknown"):
    """Store a new activity in the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Convert datetime objects to ISO strings for JSON serialization
    def serialize_datetime(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return obj

    cursor.execute(
        "INSERT INTO activities (id, activity_data, modality, created_at) VALUES (?, ?, ?, ?)",
        (
            activity_id,
            json.dumps(activity_data, default=serialize_datetime),
            modality,
            datetime.now().isoformat(),
        ),
    )
    conn.commit()
    conn.close()
    print(f"   [DB] Activity stored: {activity_id}")


def update_user_feedback(activity_id: str, feedback: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE activities SET user_feedback = ?, processed_at = ? WHERE id = ?",
        (feedback, datetime.now().isoformat(), activity_id),
    )
    conn.commit()
    conn.close()
    print(f"   [DB] Feedback stored for activity {activity_id}: {feedback[:30]}...")


def update_llm_summary(activity_id: str, summary: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE activities SET llm_summary = ?, processed_at = ? WHERE id = ?",
        (summary, datetime.now().isoformat(), activity_id),
    )
    conn.commit()
    conn.close()


def get_pending_feedback_activity():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, activity_data FROM activities WHERE user_feedback IS NULL ORDER BY created_at DESC LIMIT 1"
    )
    row = cursor.fetchone()
    conn.close()

    if row:
        return row[0], json.loads(row[1])
    return None, None
