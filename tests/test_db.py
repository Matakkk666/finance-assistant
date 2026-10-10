import pytest
from datetime import datetime
from src.models.db import TransactionDB
from src.db.repository import save_transactions
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from src.db.database import Base
from src.models.transaction import Transaction

import pytest_asyncio


@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    SessionLocal = async_sessionmaker(engine, expire_on_commit=False)
    async with SessionLocal() as session:
        yield session


@pytest.mark.asyncio
async def test_save_transactions(db_session):
    txs = [
        Transaction(
            date=datetime.now().date(),
            amount=100.0,
            description="Test 1",
            category="Food",
        ),
        Transaction(
            date=datetime.now().date(),
            amount=200.0,
            description="Test 2",
            category="Transport",
        ),
    ]
    owner_id = 12345

    await save_transactions(db_session, txs, owner_id)

    from sqlalchemy import select

    result = await db_session.execute(
        select(TransactionDB).where(TransactionDB.owner_id == owner_id)
    )
    saved_txs = result.scalars().all()

    assert len(saved_txs) == 2
    assert saved_txs[0].amount == 100.0
    assert saved_txs[1].category == "Transport"
