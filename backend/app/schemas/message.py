from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class MessageOut(BaseModel):
    id: UUID
    chat_id: UUID
    sender_id: UUID
    content: str
    reply_to_message_id: UUID | None = None
    is_edited: bool = False
    is_deleted: bool = False
    created_at: datetime
    updated_at: datetime | None = None