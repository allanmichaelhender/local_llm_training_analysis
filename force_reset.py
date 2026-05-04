#!/usr/bin/env python3
"""Force reset to catch all activities from last 7 days"""

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path(__file__).parent / "data" / "activities.db"

# Set to 7 days ago to catch all activities
new_timestamp = (datetime.now() - timedelta(days=7)).isoformat()

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute(
    "INSERT OR REPLACE INTO state (key, value) VALUES (?, ?)",
    ("last_checked", new_timestamp),
)
conn.commit()
conn.close()

print(f"Force reset last_checked to: {new_timestamp}")
print("All activities from last 7 days should now be found")
