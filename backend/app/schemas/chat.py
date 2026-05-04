from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ChatOut(BaseModel):
    id: str
    type: str  # 'private' or 'group'
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    last_message: Optional[str] = None
    last_message_time: Optional[datetime] = None
    unread_count: int = 0