import asyncio
from src.db.database import async_session
from src.models.db import TransactionDB
from sqlalchemy import select

async def main():
    async with async_session() as session:
        result = await session.execute(select(TransactionDB))
        transactions = result.scalars().all()
        print(f"Найдено транзакций в БД: {len(transactions)}")
        for t in transactions[:3]:  # покажем только первые 3
            print(f"- {t.date}: {t.description} ({t.amount} RUB) -> Категория: {t.category}")
        if len(transactions) > 3:
            print("...и еще несколько.")

if __name__ == "__main__":
    asyncio.run(main())
