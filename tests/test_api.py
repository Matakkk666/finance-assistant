import pytest
from httpx import AsyncClient, ASGITransport
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.main import app
from src.db.database import Base, get_db
from src.models.transaction import Transaction
from src.db.repository import save_transactions

import pytest_asyncio

# Create an in-memory SQLite engine for tests
test_engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
TestingSessionLocal = async_sessionmaker(test_engine, expire_on_commit=False)


async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture(autouse=True)
async def prepare_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def populate_db():
    async with TestingSessionLocal() as session:
        txs = [
            Transaction(
                date=datetime.now().date(),
                amount=-100.0,
                description="Test Food",
                category="Food",
            ),
            Transaction(
                date=datetime.now().date(),
                amount=-200.0,
                description="Test Transport",
                category="Transport",
            ),
            Transaction(
                date=datetime.now().date(),
                amount=-150.0,
                description="Test Food 2",
                category="Food",
            ),
            Transaction(
                date=datetime.now().date(),
                amount=5000.0,
                description="Salary",
                category="Income",
            ),
        ]
        await save_transactions(session, txs, 123)
        # Another user
        await save_transactions(
            session,
            [
                Transaction(
                    date=datetime.now().date(),
                    amount=-500.0,
                    description="Other",
                    category="Other",
                )
            ],
            999,
        )


@pytest.mark.asyncio
async def test_api_stats(populate_db):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/stats?user_id=123")

    assert response.status_code == 200
    data = response.json()
    assert data["total_spent"] == -450.0

    categories = data["categories"]
    assert len(categories) == 2

    # SQLite returns rows in arbitrary order, so convert to dict
    cat_dict = {c["name"]: c["value"] for c in categories}
    assert cat_dict["Food"] == -250.0
    assert cat_dict["Transport"] == -200.0


@pytest.mark.asyncio
async def test_api_transactions(populate_db):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/transactions?user_id=123&limit=2")

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 2
    assert data[0]["category"] in ["Food", "Transport", "Income"]
    assert "amount" in data[0]
