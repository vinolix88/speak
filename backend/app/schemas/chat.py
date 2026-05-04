from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime

class ChatOut(BaseModel):
    id: UUID
    type: str
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    last_message: Optional[str] = None
    last_message_time: Optional[datetime] = None
    unread_count: int = 0

class ChatCreate(BaseModel):
    type: str  # 'private' or 'group'
    name: Optional[str] = None
    participant_ids: List[UUID]  # ID участников (для private – 1 другой участник)