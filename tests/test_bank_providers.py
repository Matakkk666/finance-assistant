import pytest
import datetime
from unittest.mock import AsyncMock, patch

from src.services.bank.mock import MockBankProvider
from src.services.bank.sber import SberProvider
from src.services.bank.tbank import TBankProvider
from src.services.bank.mkb import MKBProvider
from src.services.bank.factory import get_bank_provider


@pytest.mark.asyncio
async def test_mock_bank_provider():
    provider = MockBankProvider()
    since_date = datetime.date.today() - datetime.timedelta(days=30)
    transactions = await provider.fetch_transactions(since_date)

    assert len(transactions) > 0
    assert transactions[0].amount != 0
    assert transactions[0].description
    assert isinstance(transactions[0].date, datetime.date)


@pytest.mark.asyncio
async def test_sber_provider():
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json = lambda: {
            "data": [
                {"date": "2026-10-10", "description": "Sber", "amount": -100.0}
            ]
        }
        mock_get.return_value = mock_response

        provider = SberProvider()
        transactions = await provider.fetch_transactions(datetime.date.today())
        assert len(transactions) == 1
        assert transactions[0].description == "Sber"


@pytest.mark.asyncio
async def test_tbank_provider():
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json = lambda: {
            "items": [
                {
                    "date": "2026-10-10",
                    "description": "TBank",
                    "amount": -200.0,
                }
            ]
        }
        mock_get.return_value = mock_response

        provider = TBankProvider()
        transactions = await provider.fetch_transactions(datetime.date.today())
        assert len(transactions) == 1
        assert transactions[0].description == "TBank"


@pytest.mark.asyncio
async def test_mkb_provider():
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json = lambda: {
            "transactions": [
                {"date": "2026-10-10", "description": "MKB", "amount": -300.0}
            ]
        }
        mock_get.return_value = mock_response

        provider = MKBProvider()
        transactions = await provider.fetch_transactions(datetime.date.today())
        assert len(transactions) == 1
        assert transactions[0].description == "MKB"


def test_get_bank_provider():
    assert isinstance(get_bank_provider("mock"), MockBankProvider)
    assert isinstance(get_bank_provider("sber"), SberProvider)
    assert isinstance(get_bank_provider("tbank"), TBankProvider)
    assert isinstance(get_bank_provider("mkb"), MKBProvider)

    with pytest.raises(ValueError):
        get_bank_provider("unknown")
