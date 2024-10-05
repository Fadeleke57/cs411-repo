from typing import Any, Optional
from wildlife_tracker.migration_tracking.migration_path import MigrationPath
class Migration:
    def __init__(self, migration_id: int,  start_date: str, migration_path: MigrationPath, duration: Optional[int] = None, current_date: str = None, current_location: str = None, status: str = "Scheduled") -> None:
        self.migration_id = migration_id
        self.status = status
        self.start_date = start_date
        self.duration = duration
        self.current_date = current_date
        self.current_location = current_location
        self.status = status
        self.migration_path = migration_path
