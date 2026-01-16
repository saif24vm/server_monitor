"""Data models for Server Monitor."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ResidentConfig:
    """Configuration for a single resident monitor."""
    id: str
    interval: int = 60
    upload_path: Optional[str] = None
    download_path: Optional[str] = None
    
    def __post_init__(self):
        """Set default paths if not provided."""
        if self.upload_path is None:
            self.upload_path = f"data/{self.id}_upload.json"
        if self.download_path is None:
            self.download_path = f"data/{self.id}_download.json"


@dataclass
class ResidentState:
    """Current state of a resident."""
    resident_id: str
    status: str
    timestamp: str
    
    def __repr__(self):
        return f"ResidentState({self.resident_id}, {self.status}, {self.timestamp})"
