import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.services.bank.base import BaseBankProvider
from src.services.bank.factory import get_bank_provider
from src.models.db import TransactionDB
from src.services.llm import categorize_transactions
from src.db.repository import save_transactions


async def sync_user_bank(
    owner_id: int,
    session: AsyncSession,
    provider: BaseBankProvider | None = None,
    since_date: datetime.date | None = None,
) -> dict:
    if provider is None:
        provider = get_bank_provider("mock")

    if since_date is None:
        since_date = datetime.date.today() - datetime.timedelta(days=30)

    fetched_transactions = await provider.fetch_transactions(since_date)
    if not fetched_transactions:
        return {"fetched": 0, "new": 0, "categories": {}}

    # Fetch existing to deduplicate (by date, amount, description)
    # Be careful with datetime vs date in DB
    stmt = select(TransactionDB).where(TransactionDB.owner_id == owner_id)
    # Memory deduplication
    # given the scope or we can just fetch all for owner. Let's filter by
    # since_date
    stmt = stmt.where(
        TransactionDB.date
        >= datetime.datetime.combine(since_date, datetime.time.min)
    )

    result = await session.execute(stmt)
    existing_db_txs = result.scalars().all()

    existing_signatures = set()
    for tx in existing_db_txs:
        # Note: tx.date might be datetime, we need to compare properly
        date_part = (
            tx.date.date()
            if isinstance(tx.date, datetime.datetime)
            else tx.date
        )
        sig = (date_part, tx.amount, tx.description)
        existing_signatures.add(sig)

    new_transactions = []
    for tx in fetched_transactions:
        sig = (tx.date, tx.amount, tx.description)
        if sig not in existing_signatures:
            new_transactions.append(tx)

    categories_count = {}
    if new_transactions:
        categorized = categorize_transactions(new_transactions)

        # Save to DB
        await save_transactions(session, categorized, owner_id)

        for tx in categorized:
            cat = tx.category or "Прочее"
            categories_count[cat] = categories_count.get(cat, 0) + 1

    return {
        "fetched": len(fetched_transactions),
        "new": len(new_transactions),
        "categories": categories_count,
    }
