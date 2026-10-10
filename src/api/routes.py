from datetime import datetime
from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import get_db
from src.models.db import TransactionDB, BankConnectionDB
from src.services.chat import process_user_question
from src.services.bank.sync import sync_user_bank

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


class BankConnectRequest(BaseModel):
    user_id: int
    bank_name: str


@router.get("/banks")
async def get_banks(user_id: int, db: AsyncSession = Depends(get_db)):
    banks_info = [
        {
            "id": "tbank",
            "name": "Т-Банк",
            "description": "Подключение через T-ID",
        },
        {
            "id": "sber",
            "name": "Сбер",
            "description": "Подключение через Sber ID",
        },
        {
            "id": "mkb",
            "name": "МКБ",
            "description": "Подключение через MKB",
        },
        {
            "id": "mock",
            "name": "Mock Bank",
            "description": "Для тестирования",
        },
    ]
    query = select(BankConnectionDB).where(
        BankConnectionDB.user_id == user_id
    )
    result = await db.execute(query)
    connections = {conn.bank_name: conn for conn in result.scalars().all()}

    response = []
    for b in banks_info:
        conn = connections.get(b["id"])
        is_connected = conn is not None and conn.status == "connected"
        synced_at = None
        if conn and conn.last_synced_at:
            synced_at = conn.last_synced_at.isoformat()
        response.append({
            "id": b["id"],
            "name": b["name"],
            "description": b["description"],
            "is_connected": is_connected,
            "last_synced_at": synced_at,
        })
    return response


@router.post("/banks/connect")
async def connect_bank(request: BankConnectRequest):
    auth_url = (
        f"/api/banks/auth-screen?bank={request.bank_name}"
        f"&user_id={request.user_id}"
    )
    return {"auth_url": auth_url}


@router.get("/banks/auth-screen", response_class=HTMLResponse)
async def auth_screen(bank: str, user_id: int):
    cb_url = f"/api/banks/callback?bank={bank}&user_id={user_id}&code=success"
    return f"""
    <html>
        <body>
            <h1>Вход через {bank.capitalize()} ID</h1>
            <p>Мы запрашиваем доступ к вашим операциям.</p>
            <a href="{cb_url}">
                <button>Одобрить доступ</button>
            </a>
        </body>
    </html>
    """


@router.get("/banks/callback", response_class=HTMLResponse)
async def auth_callback(
        bank: str,
        user_id: int,
        code: str,
        db: AsyncSession = Depends(get_db)):
    if code == "success":
        query = select(BankConnectionDB).where(
            BankConnectionDB.user_id == user_id,
            BankConnectionDB.bank_name == bank
        )
        result = await db.execute(query)
        conn = result.scalar_one_or_none()

        if conn:
            conn.status = "connected"
        else:
            conn = BankConnectionDB(
                user_id=user_id,
                bank_name=bank,
                status="connected")
            db.add(conn)
        await db.commit()

        return """
        <html>
            <body>
                <h1>Успешно!</h1>
                <script>
                    window.close();
                </script>
            </body>
        </html>
        """
    return "Error"


@router.post("/banks/sync")
async def sync_bank(
        request: BankConnectRequest,
        db: AsyncSession = Depends(get_db)):
    query = select(BankConnectionDB).where(
        BankConnectionDB.user_id == request.user_id,
        BankConnectionDB.bank_name == request.bank_name
    )
    result = await db.execute(query)
    conn = result.scalar_one_or_none()

    if not conn or conn.status != "connected":
        return {"status": "error", "message": "Bank not connected"}

    await sync_user_bank(request.user_id, db)

    conn.last_synced_at = datetime.utcnow()
    await db.commit()

    return {"status": "ok"}


@router.post("/banks/disconnect")
async def disconnect_bank(
        request: BankConnectRequest,
        db: AsyncSession = Depends(get_db)):
    query = select(BankConnectionDB).where(
        BankConnectionDB.user_id == request.user_id,
        BankConnectionDB.bank_name == request.bank_name
    )
    result = await db.execute(query)
    conn = result.scalar_one_or_none()

    if conn:
        conn.status = "disconnected"
        await db.commit()

    return {"status": "ok"}
