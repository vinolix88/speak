from sqlalchemy import String, DateTime, func, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from app.db.base import Base
import uuid

class ChatParticipant(Base):
    __tablename__ = "chat_participants"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    chat_id: Mapped[str] = mapped_column(String(36), ForeignKey("chats.id"), nullable=False)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    role: Mapped[str] = mapped_column(SQLEnum('member', 'admin', 'creator', name='participant_role'), default='member')
    joined_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    last_read_message_id: Mapped[str] = mapped_column(String(36), nullable=True)