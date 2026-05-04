#!/usr/bin/env python3
"""Add missing modality column to existing database"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "data" / "activities.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

try:
    # Check if modality column exists
    cursor.execute("PRAGMA table_info(activities)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if "modality" not in columns:
        print("Adding modality column to activities table...")
        cursor.execute("ALTER TABLE activities ADD COLUMN modality TEXT")
        conn.commit()
        print("Column added successfully")
    else:
        print("modality column already exists")
        
except Exception as e:
    print(f"Error: {e}")
    conn.rollback()
finally:
    conn.close()
