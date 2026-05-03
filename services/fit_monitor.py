"""
FIT file monitoring service.
Watches for new .fit files and processes them for workout analysis.
"""

import os
from datetime import datetime, timedelta
from typing import List, Dict

from .fit_processor import FITProcessor
from .database import is_activity_processed, store_activity


class FITMonitor:
    """Monitor FIT files for new workouts."""

    def __init__(self):
        self.processor = FITProcessor()
        self.last_check = datetime.now() - timedelta(hours=1)  # Start 1 hour ago

    def check_for_new_workouts(self) -> List[Dict]:
        """Check for new FIT files and return unprocessed activities."""
        new_activities = []

        if not self.processor.is_device_connected():
            return new_activities

        # Find files modified since last check
        new_files = self.processor.find_new_files(self.last_check)

        for filepath in new_files:
            # Generate activity ID to check if already processed
            activity_id = self._generate_file_id(filepath)

            if not is_activity_processed(activity_id):
                activity = self.processor.parse_file(filepath)
                if activity:
                    # Store in database
                    store_activity(activity_id, activity)
                    new_activities.append(activity)

        self.last_check = datetime.now()
        return new_activities

    def _generate_file_id(self, filepath: str) -> str:
        """Generate consistent ID for a FIT file."""
        # Use file modification time + filename for unique ID
        mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
        filename = os.path.basename(filepath)
        return f"fit_{mtime.strftime('%Y%m%d_%H%M%S')}_{filename}"
