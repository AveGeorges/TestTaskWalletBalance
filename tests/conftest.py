from decimal import Decimal

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import settings

# Engine создаём до импорта app, чтобы не привязываться к чужому event loop
test_engine = create_async_engine(settings.database_url, poolclass=NullPool)
TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    class_=AsyncSession,
)

import app.db.session as db_session

db_session.engine = test_engine
db_session.AsyncSessionLocal = TestSessionLocal

from app.db.session import get_db
from app.main import app
from app.models.models import Wallet
from app.seed.constants import WALLET_UUID_MAIN


@pytest.fixture(scope="session", autouse=True)
async def dispose_test_engine():
    yield
    await test_engine.dispose()


@pytest.fixture(autouse=True)
async def clean_database():
    async with test_engine.begin() as conn:
        await conn.execute(text("TRUNCATE TABLE operations, wallets RESTART IDENTITY CASCADE"))
    yield


@pytest.fixture
async def client():
    async def override_get_db():
        async with TestSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
async def wallet_uuid() -> str:
    async with TestSessionLocal() as session:
        session.add(Wallet(uuid=WALLET_UUID_MAIN, balance=Decimal("1000.00")))
        await session.commit()
    return str(WALLET_UUID_MAIN)
