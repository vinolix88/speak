import asyncio
import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.core.config import settings

async def add_data():
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    async with engine.connect() as conn:
        chat_id = "10f576ad-64f6-4049-87b2-fb96f56e4c2d"
        user1 = "70c961eb-623c-43af-a24d-aa3cfd3a10ed"
        user2 = "30cbcd70-b2f1-489c-bd96-a7b4402019b6"

        # Удалим старых участников, чтобы избежать дублей (на случай, если уже есть)
        await conn.execute(text("DELETE FROM chat_participants WHERE chat_id = :chat_id"), {"chat_id": chat_id})

        # Добавляем участников
        for user_id in (user1, user2):
            await conn.execute(
                text("INSERT INTO chat_participants (id, chat_id, user_id, role, joined_at) VALUES (:id, :chat_id, :user_id, 'member', :joined_at)"),
                {"id": str(uuid.uuid4()), "chat_id": chat_id, "user_id": user_id, "joined_at": datetime.now()}
            )

        # Добавляем сообщения
        messages = [
            (user1, "Привет!"),
            (user2, "Здравствуй!"),
            (user1, "Как дела?"),
            (user2, "Отлично, а у тебя?"),
            (user1, "Тоже хорошо! Давай созвонимся позже."),
        ]
        for sender, content in messages:
            await conn.execute(
                text("INSERT INTO messages (id, chat_id, sender_id, content, created_at) VALUES (:id, :chat_id, :sender_id, :content, :created_at)"),
                {"id": str(uuid.uuid4()), "chat_id": chat_id, "sender_id": sender, "content": content, "created_at": datetime.now()}
            )

        await conn.commit()
        print(f"Тестовые данные добавлены в чат {chat_id}")

    await engine.dispose()

asyncio.run(add_data())