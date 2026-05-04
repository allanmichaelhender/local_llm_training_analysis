#!/usr/bin/env python3
"""Clear database for fresh testing"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "data" / "activities.db"

if DB_PATH.exists():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Clear activities table
    cursor.execute("DELETE FROM activities")
    print("Cleared activities table")
    
    # Reset state
    cursor.execute("DELETE FROM state WHERE key = 'last_checked'")
    print("Reset last_checked timestamp")
    
    conn.commit()
    conn.close()
    print("Database cleared successfully")
else:
    print("Database does not exist - creating new one")
