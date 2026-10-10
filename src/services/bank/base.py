import datetime
from abc import ABC, abstractmethod
from src.models.transaction import Transaction


class BaseBankProvider(ABC):
    @abstractmethod
    async def fetch_transactions(
        self, since_date: datetime.date
    ) -> list[Transaction]:
        pass
