from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from app.db.session import get_db
from app.db.models.users import User
from app.db.models.chats import Chat
from app.db.models.chat_participants import ChatParticipant
from app.db.models.messages import Message
from app.schemas.chat import ChatOut
from app.core.security import get_current_user
from typing import List

router = APIRouter(prefix="/chats", tags=["chats"])

@router.get("", response_model=List[ChatOut])
async def get_user_chats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # 1. Получаем ID чатов, где пользователь участник
    subq = select(ChatParticipant.chat_id).where(ChatParticipant.user_id == current_user.id)
    result = await db.execute(select(Chat).where(Chat.id.in_(subq)))
    chats = result.scalars().all()

    response = []
    for chat in chats:
        # Для личного чата: подставляем имя и аватар собеседника
        if chat.type == 'private':
            # Находим другого участника
            participants = await db.execute(
                select(ChatParticipant.user_id).where(ChatParticipant.chat_id == chat.id)
            )
            user_ids = participants.scalars().all()
            other_id = next((uid for uid in user_ids if uid != current_user.id), None)
            if other_id:
                other_user = await db.execute(select(User).where(User.id == other_id))
                other = other_user.scalar_one_or_none()
                chat_name = other.username if other else "Unknown"
                avatar_url = other.avatar_url if other else None
            else:
                chat_name = "Chat"
                avatar_url = None
        else:
            chat_name = chat.name
            avatar_url = None  # позже добавим avatar_url в таблицу chats

        # 2. Последнее сообщение
        last_msg = await db.execute(
            select(Message).where(Message.chat_id == chat.id).order_by(Message.created_at.desc()).limit(1)
        )
        last = last_msg.scalar_one_or_none()

        # 3. Количество непрочитанных (если last_read_message_id не задано – считаем все)
        participant = await db.execute(
            select(ChatParticipant).where(and_(
                ChatParticipant.chat_id == chat.id,
                ChatParticipant.user_id == current_user.id
            ))
        )
        part = participant.scalar_one_or_none()
        if part and part.last_read_message_id:
            unread = await db.execute(
                select(func.count(Message.id)).where(
                    and_(Message.chat_id == chat.id, Message.id > part.last_read_message_id)
                )
            )
            unread_count = unread.scalar_one() or 0
        else:
            # Нет отметки о прочитанном – считаем все сообщения непрочитанными
            total_msgs = await db.execute(
                select(func.count(Message.id)).where(Message.chat_id == chat.id)
            )
            unread_count = total_msgs.scalar_one() or 0

        response.append(ChatOut(
            id=chat.id,
            type=chat.type,
            name=chat_name,
            avatar_url=avatar_url,
            last_message=last.content if last else None,
            last_message_time=last.created_at if last else None,
            unread_count=unread_count
        ))

    return response