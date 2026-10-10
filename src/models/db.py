import uuid
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from src.db.database import Base


class TransactionDB(Base):
    __tablename__ = "transactions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    owner_id: Mapped[int] = mapped_column()
    date: Mapped[datetime] = mapped_column()
    amount: Mapped[float] = mapped_column()
    description: Mapped[str] = mapped_column()
    category: Mapped[str] = mapped_column()


class BankConnectionDB(Base):
    __tablename__ = "bank_connections"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[int] = mapped_column()
    bank_name: Mapped[str] = mapped_column()
    status: Mapped[str] = mapped_column(default="connected")
    connected_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    last_synced_at: Mapped[datetime | None] = mapped_column(
        nullable=True, default=None
    )
