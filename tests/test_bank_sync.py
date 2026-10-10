import pytest
import datetime
from unittest.mock import AsyncMock, patch, MagicMock

from src.models.transaction import Transaction
from src.services.bank.sync import sync_user_bank
from src.services.bank.base import BaseBankProvider
from src.models.db import TransactionDB


class DummyProvider(BaseBankProvider):
    async def fetch_transactions(
        self, since_date: datetime.date
    ) -> list[Transaction]:
        return [
            Transaction(
                date=datetime.date(2026, 10, 10),
                description="Existing",
                amount=-100.0,
            ),
            Transaction(
                date=datetime.date(2026, 10, 10),
                description="New",
                amount=-50.0,
            ),
        ]


@pytest.fixture
def mock_session():
    session = AsyncMock()
    # Mock execute to return existing transactions
    mock_result = MagicMock()
    existing_tx = TransactionDB(
        owner_id=1,
        date=datetime.datetime(2026, 10, 10),
        amount=-100.0,
        description="Existing",
        category="Test",
    )
    mock_result.scalars().all.return_value = [existing_tx]
    session.execute.return_value = mock_result
    return session


@pytest.mark.asyncio
@patch("src.services.bank.sync.categorize_transactions")
async def test_sync_user_bank_deduplication(mock_categorize, mock_session):
    mock_categorize.return_value = [
        Transaction(
            date=datetime.date(2026, 10, 10),
            description="New",
            amount=-50.0,
            category="TestCat",
        )
    ]

    provider = DummyProvider()
    result = await sync_user_bank(
        owner_id=1,
        session=mock_session,
        provider=provider,
        since_date=datetime.date(2026, 10, 1),
    )

    assert result["fetched"] == 2
    assert result["new"] == 1
    assert result["categories"]["TestCat"] == 1

    # Check that categorize was called with only the new transaction
    called_txs = mock_categorize.call_args[0][0]
    assert len(called_txs) == 1
    assert called_txs[0].description == "New"

    # Check that session.add was called once
    assert mock_session.add.call_count == 1
    added_db_tx = mock_session.add.call_args[0][0]
    assert added_db_tx.description == "New"
