from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import get_db
from src.models.db import TransactionDB
from src.services.chat import process_user_question

router = APIRouter(prefix="/api")


class ChatRequest(BaseModel):
    user_id: int
    message: str


@router.get("/stats")
async def get_stats(user_id: int, db: AsyncSession = Depends(get_db)):
    # Calculate total spent (only expenses)
    total_query = select(func.sum(TransactionDB.amount)).where(
        TransactionDB.owner_id == user_id, TransactionDB.amount < 0
    )
    total_result = await db.execute(total_query)
    total_spent = total_result.scalar() or 0.0

    # Calculate categories (only expenses)
    cat_query = (
        select(TransactionDB.category, func.sum(TransactionDB.amount))
        .where(TransactionDB.owner_id == user_id, TransactionDB.amount < 0)
        .group_by(TransactionDB.category)
    )
    cat_result = await db.execute(cat_query)
    categories = [
        {"name": row[0], "value": float(row[1])} for row in cat_result.all()
    ]

    return {"total_spent": float(total_spent), "categories": categories}


@router.get("/transactions")
async def get_transactions(
    user_id: int, limit: int = 1000, db: AsyncSession = Depends(get_db)
):
    query = (
        select(TransactionDB)
        .where(TransactionDB.owner_id == user_id)
        .order_by(TransactionDB.date.desc())
        .limit(limit)
    )
    result = await db.execute(query)
    transactions = result.scalars().all()
    return [
        {
            "id": t.id,
            "date": t.date.isoformat(),
            "amount": float(t.amount),
            "description": t.description,
            "category": t.category,
        }
        for t in transactions
    ]


@router.post("/chat")
async def chat(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    answer = await process_user_question(request.message, request.user_id, db)
    return {"answer": answer}
