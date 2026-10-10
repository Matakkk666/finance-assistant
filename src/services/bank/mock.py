import datetime
from src.services.bank.base import BaseBankProvider
from src.models.transaction import Transaction


class MockBankProvider(BaseBankProvider):
    async def fetch_transactions(
        self, since_date: datetime.date
    ) -> list[Transaction]:
        return [
            Transaction(
                date=since_date + datetime.timedelta(days=1),
                description="Test Transaction 1",
                amount=-150.0,
            ),
            Transaction(
                date=since_date + datetime.timedelta(days=2),
                description="Test Transaction 2",
                amount=2000.0,
            ),
        ]
