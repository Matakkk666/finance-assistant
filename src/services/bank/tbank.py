import datetime
import httpx
from src.services.bank.base import BaseBankProvider
from src.models.transaction import Transaction


class TBankProvider(BaseBankProvider):
    async def fetch_transactions(
        self, since_date: datetime.date
    ) -> list[Transaction]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.tbank.ru/v1/transactions",
                params={"since": since_date.isoformat()},
            )
            if response.status_code == 200:
                data = response.json()
                return [
                    Transaction(
                        date=datetime.date.fromisoformat(item["date"]),
                        description=item["description"],
                        amount=item["amount"],
                    )
                    for item in data.get("items", [])
                ]
            return []
