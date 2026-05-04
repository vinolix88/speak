from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from app.db.session import get_db
from app.db.models.users import User
from app.db.models.messages import Message
from app.db.models.chats import Chat
from app.db.models.chat_participants import ChatParticipant
from app.schemas.message import MessageOut
from app.core.security import get_current_user
from typing import List
from uuid import UUID
from app.schemas.chat import ChatOut
from app.api.v1.endpoints.chats import _build_chat_response

router = APIRouter(prefix="/search", tags=["search"])


@router.get("/messages", response_model=List[MessageOut])
async def search_messages(
    q: str = Query(..., min_length=1, description="Поисковый запрос"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Находим все чаты, где участвует пользователь
    subq = select(ChatParticipant.chat_id).where(
        ChatParticipant.user_id == current_user.id
    )
    # Ищем сообщения в этих чатах, где content содержит q (регистронезависимо)
    stmt = (
        select(Message)
        .where(Message.chat_id.in_(subq), Message.content.ilike(f"%{q}%"))
        .order_by(Message.created_at.desc())
        .limit(50)
    )
    result = await db.execute(stmt)
    messages = result.scalars().all()
    return messages


@router.get("/chats", response_model=List[ChatOut])
async def search_chats(
    q: str = Query(..., min_length=1),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Получаем все чаты пользователя
    subq = select(ChatParticipant.chat_id).where(
        ChatParticipant.user_id == current_user.id
    )
    chats_result = await db.execute(select(Chat).where(Chat.id.in_(subq)))
    chats = chats_result.scalars().all()

    result = []
    for chat in chats:
        if chat.type == "group" and chat.name and q.lower() in chat.name.lower():
            result.append(chat)
        elif chat.type == "private":
            # Находим собеседника
            part = await db.execute(
                select(ChatParticipant.user_id).where(
                    ChatParticipant.chat_id == chat.id
                )
            )
            user_ids = part.scalars().all()
            other_id = next((uid for uid in user_ids if uid != current_user.id), None)
            if other_id:
                other = await db.execute(select(User).where(User.id == other_id))
                other_user = other.scalar_one_or_none()
                if other_user and q.lower() in other_user.username.lower():
                    result.append(chat)
    responses = []
    for chat in result:
        responses.append(await _build_chat_response(chat, current_user.id, db))
    return responses
