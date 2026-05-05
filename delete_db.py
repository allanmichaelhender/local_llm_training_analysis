import os
from pathlib import Path

db_path = Path(__file__).parent / "data" / "activities.db"
if db_path.exists():
    os.remove(db_path)
    print(f"Deleted: {db_path}")
else:
    print(f"File not found: {db_path}")
