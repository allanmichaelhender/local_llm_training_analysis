#!/usr/bin/env python3
"""Reset the last_checked timestamp to see missing activities"""

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path(__file__).parent / "data" / "activities.db"

# Set last_checked to 3 days ago to catch missing activities
new_timestamp = (datetime.now() - timedelta(days=3)).isoformat()

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute(
    "INSERT OR REPLACE INTO state (key, value) VALUES (?, ?)",
    ("last_checked", new_timestamp),
)
conn.commit()
conn.close()

print(f"Reset last_checked to: {new_timestamp}")
print("Now restart the app to see the missing activities")
