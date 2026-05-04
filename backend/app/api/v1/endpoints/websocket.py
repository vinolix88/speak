from fastapi import WebSocket, WebSocketDisconnect, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from jose import jwt, JWTError
from app.db.session import get_db
from app.db.models.users import User
from app.db.models.chats import Chat
from app.db.models.chat_participants import ChatParticipant
from app.db.models.messages import Message
from app.core.config import settings
import uuid
from datetime import datetime

# Хранилище активных WebSocket соединений (в памяти, для MVP)
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}  # chat_id -> list of websockets

    async def connect(self, websocket: WebSocket, chat_id: str):
        await websocket.accept()
        if chat_id not in self.active_connections:
            self.active_connections[chat_id] = []
        self.active_connections[chat_id].append(websocket)

    def disconnect(self, websocket: WebSocket, chat_id: str):
        if chat_id in self.active_connections:
            self.active_connections[chat_id].remove(websocket)
            if not self.active_connections[chat_id]:
                del self.active_connections[chat_id]

    async def broadcast(self, chat_id: str, message: dict):
        if chat_id in self.active_connections:
            for connection in self.active_connections[chat_id]:
                await connection.send_json(message)

manager = ConnectionManager()

async def get_current_user_ws(token: str, db: AsyncSession):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(401, "Invalid token")
    except JWTError:
        raise HTTPException(401, "Invalid token")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(401, "User not found")
    return user

async def websocket_chat(websocket: WebSocket, chat_id: str, token: str, db: AsyncSession = Depends(get_db)):
    # Аутентификация
    try:
        current_user = await get_current_user_ws(token, db)
    except HTTPException:
        await websocket.close(code=1008)
        return

    # Проверка, является ли пользователь участником чата
    participant = await db.execute(
        select(ChatParticipant).where(
            and_(
                ChatParticipant.chat_id == chat_id,
                ChatParticipant.user_id == current_user.id
            )
        )
    )
    if not participant.scalar_one_or_none():
        await websocket.close(code=1008)
        return

    await manager.connect(websocket, chat_id)

    try:
        while True:
            data = await websocket.receive_json()
            content = data.get("content")
            if not content:
                continue

            # Сохраняем сообщение в базу
            new_message = Message(
                id=str(uuid.uuid4()),
                chat_id=chat_id,
                sender_id=current_user.id,
                content=content,
                reply_to_message_id=None,
                is_edited=False,
                is_deleted=False,
                created_at=datetime.utcnow(),
                updated_at=None
            )
            db.add(new_message)
            await db.commit()

            # Обновляем updated_at в чате (опционально)
            chat = await db.get(Chat, chat_id)
            if chat:
                chat.updated_at = datetime.utcnow()
                db.add(chat)
                await db.commit()

            # Формируем ответ для трансляции
            response = {
                "id": str(new_message.id),
                "chat_id": chat_id,
                "sender_id": current_user.id,
                "sender_username": current_user.username,
                "content": content,
                "created_at": new_message.created_at.isoformat(),
            }
            await manager.broadcast(chat_id, response)

    except WebSocketDisconnect:
        manager.disconnect(websocket, chat_id)