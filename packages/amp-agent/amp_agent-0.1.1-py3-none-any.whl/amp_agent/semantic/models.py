"""
Core models for the agent system.
"""
from dataclasses import dataclass
from typing import Dict, Any, Optional
from datetime import datetime

@dataclass
class Message:
    """
    Represents a message in the system.
    """
    id: str
    content: str
    metadata: Dict[str, Any]
    created_at: Optional[datetime] = None
    channel_id: Optional[str] = None
    user_id: Optional[str] = None 