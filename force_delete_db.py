import os
from pathlib import Path

db_path = Path("data/activities.db")
if db_path.exists():
    os.remove(db_path)
    print(f"Deleted: {db_path}")
else:
    print(f"File does not exist: {db_path}")
