import pytest
from unittest.mock import patch
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.main import app
from src.db.database import Base, get_db
from src.models.db import BankConnectionDB

import pytest_asyncio

test_engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
TestingSessionLocal = async_sessionmaker(test_engine, expire_on_commit=False)


async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session


@pytest_asyncio.fixture(autouse=True)
async def prepare_database():
    app.dependency_overrides[get_db] = override_get_db
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    app.dependency_overrides.pop(get_db, None)


@pytest.mark.asyncio
async def test_db_bank_connection():
    async with TestingSessionLocal() as session:
        bank = BankConnectionDB(
            user_id=123,
            bank_name="tbank",
            status="connected"
        )
        session.add(bank)
        await session.commit()

        query = select(BankConnectionDB).where(BankConnectionDB.user_id == 123)
        result = await session.execute(query)
        record = result.scalar_one_or_none()

        assert record is not None
        assert record.bank_name == "tbank"
        assert record.status == "connected"


@pytest.mark.asyncio
async def test_get_banks():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/banks?user_id=123")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    banks = [b["id"] for b in data]
    assert "tbank" in banks
    assert "sber" in banks
    assert "mkb" in banks
    assert data[0]["is_connected"] is False


@pytest.mark.asyncio
async def test_connect_bank():
    transport = ASGITransport(app=app)
    payload = {"user_id": 123, "bank_name": "tbank"}
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/api/banks/connect", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert "auth_url" in data
    assert "/api/banks/auth-screen" in data["auth_url"]


@pytest.mark.asyncio
async def test_auth_screen():
    transport = ASGITransport(app=app)
    url = "/api/banks/auth-screen?bank=tbank&user_id=123"
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get(url)

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Одобрить доступ" in response.text


@pytest.mark.asyncio
async def test_callback():
    transport = ASGITransport(app=app)
    url = "/api/banks/callback?bank=tbank&user_id=123&code=success"
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get(url)

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

    async with TestingSessionLocal() as session:
        query = select(BankConnectionDB).where(BankConnectionDB.user_id == 123)
        result = await session.execute(query)
        record = result.scalar_one_or_none()
        assert record is not None
        assert record.status == "connected"


@pytest.mark.asyncio
@patch("src.api.routes.sync_user_bank")
async def test_sync_bank(mock_sync):
    mock_sync.return_value = {
        "fetched": 2,
        "new": 1,
        "categories": {"Food": 1},
    }
    async with TestingSessionLocal() as session:
        bank = BankConnectionDB(
            user_id=123,
            bank_name="tbank",
            status="connected")
        session.add(bank)
        await session.commit()

    transport = ASGITransport(app=app)
    payload = {"user_id": 123, "bank_name": "tbank"}
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/api/banks/sync", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    mock_sync.assert_called_once()

    async with TestingSessionLocal() as session:
        query = select(BankConnectionDB).where(BankConnectionDB.user_id == 123)
        result = await session.execute(query)
        record = result.scalar_one_or_none()
        assert record.last_synced_at is not None


@pytest.mark.asyncio
async def test_disconnect_bank():
    async with TestingSessionLocal() as session:
        bank = BankConnectionDB(
            user_id=123,
            bank_name="tbank",
            status="connected")
        session.add(bank)
        await session.commit()

    transport = ASGITransport(app=app)
    payload = {"user_id": 123, "bank_name": "tbank"}
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/api/banks/disconnect", json=payload)

    assert response.status_code == 200

    async with TestingSessionLocal() as session:
        query = select(BankConnectionDB).where(BankConnectionDB.user_id == 123)
        result = await session.execute(query)
        record = result.scalar_one_or_none()
        assert record.status == "disconnected"
