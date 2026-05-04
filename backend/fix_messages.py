import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.core.config import settings

async def fix():
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    async with engine.connect() as conn:
        await conn.execute(text("ALTER TABLE messages ALTER COLUMN is_edited SET DEFAULT FALSE"))
        await conn.execute(text("ALTER TABLE messages ALTER COLUMN is_deleted SET DEFAULT FALSE"))
        await conn.execute(text("ALTER TABLE messages ALTER COLUMN is_edited SET NOT NULL"))
        await conn.execute(text("ALTER TABLE messages ALTER COLUMN is_deleted SET NOT NULL"))
        await conn.commit()
        print("Defaults added and NOT NULL enforced")
    await engine.dispose()

asyncio.run(fix())