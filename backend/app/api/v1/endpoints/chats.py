from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from app.db.session import get_db
from app.db.models.users import User
from app.db.models.chats import Chat
from app.db.models.chat_participants import ChatParticipant
from app.db.models.messages import Message
from app.schemas.chat import ChatOut, ChatCreate
from app.core.security import get_current_user
from typing import List
import uuid
from datetime import datetime

router = APIRouter(prefix="/chats", tags=["chats"])

# --- Вспомогательная функция для формирования ответа ---
async def _build_chat_response(chat: Chat, current_user_id: str, db: AsyncSession) -> ChatOut:
    # Для private чата подставляем имя и аватар собеседника
    if chat.type == 'private':
        # Найдём другого участника
        participants = await db.execute(
            select(ChatParticipant.user_id).where(ChatParticipant.chat_id == chat.id)
        )
        user_ids = participants.scalars().all()
        other_id = next((uid for uid in user_ids if uid != current_user_id), None)
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
        avatar_url = None

    # Последнее сообщение
    last_msg = await db.execute(
        select(Message).where(Message.chat_id == chat.id).order_by(Message.created_at.desc()).limit(1)
    )
    last = last_msg.scalar_one_or_none()

    # Количество непрочитанных
    participant = await db.execute(
        select(ChatParticipant).where(and_(
            ChatParticipant.chat_id == chat.id,
            ChatParticipant.user_id == current_user_id
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
        total = await db.execute(select(func.count(Message.id)).where(Message.chat_id == chat.id))
        unread_count = total.scalar_one() or 0

    return ChatOut(
        id=chat.id,
        type=chat.type,
        name=chat_name,
        avatar_url=avatar_url,
        last_message=last.content if last else None,
        last_message_time=last.created_at if last else None,
        unread_count=unread_count
    )

# --- GET /chats (список чатов пользователя) ---
@router.get("", response_model=List[ChatOut])
async def get_user_chats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    subq = select(ChatParticipant.chat_id).where(ChatParticipant.user_id == current_user.id)
    result = await db.execute(select(Chat).where(Chat.id.in_(subq)))
    chats = result.scalars().all()

    responses = []
    for chat in chats:
        responses.append(await _build_chat_response(chat, current_user.id, db))
    return responses

# --- POST /chats (создание чата) ---
@router.post("", response_model=ChatOut)
async def create_chat(
    chat_data: ChatCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Проверка: для личного чата нужен ровно один другой участник
    if chat_data.type == 'private':
        if len(chat_data.participant_ids) != 1:
            raise HTTPException(400, "Private chat must have exactly one other participant")
        other_id = str(chat_data.participant_ids[0])

        # Проверяем, существует ли уже чат между этими двумя
        # Найдём все чаты, где текущий пользователь участник
        subq = select(ChatParticipant.chat_id).where(ChatParticipant.user_id == current_user.id)
        stmt = select(Chat.id).where(
            Chat.type == 'private',
            Chat.id.in_(subq),
            Chat.id.in_(select(ChatParticipant.chat_id).where(ChatParticipant.user_id == other_id))
        )
        existing = await db.execute(stmt)
        existing_id = existing.scalar_one_or_none()
        if existing_id:
            # Вернуть существующий чат
            chat = await db.get(Chat, existing_id)
            return await _build_chat_response(chat, current_user.id, db)

        # Создаём новый чат
        new_chat = Chat(
            id=str(uuid.uuid4()),
            type='private',
            name=None,
            created_by=current_user.id,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db.add(new_chat)
        await db.flush()

        # Добавляем участников
        for uid in [current_user.id, other_id]:
            participant = ChatParticipant(
                id=str(uuid.uuid4()),
                chat_id=new_chat.id,
                user_id=uid,
                role='member',
                joined_at=datetime.now()
            )
            db.add(participant)
        await db.commit()
        await db.refresh(new_chat)
        return await _build_chat_response(new_chat, current_user.id, db)

    else:
        # Групповой чат – пока заглушка
        raise HTTPException(501, "Group chat creation not implemented yet")

# --- GET /chats/{chat_id} (детали чата) ---
@router.get("/{chat_id}", response_model=ChatOut)
async def get_chat_detail(
    chat_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    chat = await db.get(Chat, chat_id)
    if not chat:
        raise HTTPException(404, "Chat not found")
    # Проверяем, участник ли пользователь
    participant = await db.execute(
        select(ChatParticipant).where(and_(
            ChatParticipant.chat_id == chat_id,
            ChatParticipant.user_id == current_user.id
        ))
    )
    if not participant.scalar_one_or_none():
        raise HTTPException(403, "Access denied")
    return await _build_chat_response(chat, current_user.id, db)