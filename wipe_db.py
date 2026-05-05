#!/usr/bin/env python3
"""Wipe database completely"""

import os
from pathlib import Path

DB_PATH = Path(__file__).parent / "data" / "activities.db"

if DB_PATH.exists():
    os.remove(DB_PATH)
    print(f"Database deleted: {DB_PATH}")
else:
    print(f"Database does not exist: {DB_PATH}")
