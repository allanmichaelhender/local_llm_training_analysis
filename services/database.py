import sqlite3
import json
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "activities.db"


def init_db():
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS activities (
            id TEXT PRIMARY KEY,
            garmin_data TEXT,
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
    return datetime.min


def set_last_checked(timestamp: datetime):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO state (key, value) VALUES (?, ?)",
        ("last_checked", timestamp.isoformat())
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


def store_activity(activity_id: str, garmin_data: dict):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO activities (id, garmin_data) VALUES (?, ?)",
        (activity_id, json.dumps(garmin_data))
    )
    conn.commit()
    conn.close()


def update_user_feedback(activity_id: str, feedback: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE activities SET user_feedback = ? WHERE id = ?",
        (feedback, activity_id)
    )
    conn.commit()
    conn.close()


def update_llm_summary(activity_id: str, summary: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE activities SET llm_summary = ?, processed_at = ? WHERE id = ?",
        (summary, datetime.now().isoformat(), activity_id)
    )
    conn.commit()
    conn.close()


def get_pending_feedback_activity():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, garmin_data FROM activities WHERE user_feedback IS NULL ORDER BY created_at DESC LIMIT 1"
    )
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return row[0], json.loads(row[1])
    return None, None
