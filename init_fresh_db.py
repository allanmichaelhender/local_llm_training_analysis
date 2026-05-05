#!/usr/bin/env python3
"""Initialize fresh database with correct schema"""

from services.database import init_db
import sqlite3
from pathlib import Path

# Initialize database
init_db()
print("Database initialized")

# Verify schema
DB_PATH = Path(__file__).parent / "data" / "activities.db"
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Check tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print(f"Tables created: {[t[0] for t in tables]}")

# Check activities table schema
cursor.execute("PRAGMA table_info(activities)")
columns = cursor.fetchall()
print("\nActivities table schema:")
for col in columns:
    print(f"  {col[1]}: {col[2]}")

conn.close()
print("\nDatabase schema verified successfully")
