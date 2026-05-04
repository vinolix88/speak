import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.main import app
from httpx import AsyncClient, ASGITransport
from app.db.session import get_db
from app.core.config import settings

DATABASE_URL = settings.DATABASE_URL

@pytest.fixture(scope="session")
def event_loop():
    import asyncio
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="session")
async def engine():
    engine = create_async_engine(DATABASE_URL, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()

@pytest_asyncio.fixture
async def db_session(engine):
    async with engine.connect() as conn:
        await conn.begin()
        async_session = sessionmaker(bind=conn, class_=AsyncSession, expire_on_commit=False)
        session = async_session()
        yield session
        await session.rollback()
        await conn.rollback()
        await session.close()

@pytest_asyncio.fixture
async def client(db_session):
    async def get_db_override():
        yield db_session
    app.dependency_overrides[get_db] = get_db_override
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()