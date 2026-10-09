from sqlalchemy.ext.asyncio import AsyncSession
from src.models.transaction import Transaction
from src.models.db import TransactionDB
from typing import List


async def save_transactions(
        session: AsyncSession,
        transactions: List[Transaction],
        owner_id: int):
    for tx in transactions:
        db_tx = TransactionDB(
            owner_id=owner_id,
            date=tx.date,
            amount=tx.amount,
            description=tx.description,
            category=tx.category
        )
        session.add(db_tx)
    await session.commit()
