import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.core.config import settings

async def reset():
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    async with engine.connect() as conn:
        await conn.execute(text("DROP SCHEMA public CASCADE"))
        await conn.execute(text("CREATE SCHEMA public"))
        await conn.commit()
        print("Schema public dropped and recreated.")
    await engine.dispose()

asyncio.run(reset())