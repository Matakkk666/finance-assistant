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
