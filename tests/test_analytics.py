import datetime

from src.models.transaction import Transaction
from src.services.analytics import aggregate_by_category


def test_aggregate_by_category():
    txs = [
        Transaction(
            date=datetime.date(2026, 1, 1),
            description="Такси",
            amount=-500,
            category="Транспорт",
        ),
        Transaction(
            date=datetime.date(2026, 1, 2),
            description="Автобус",
            amount=-50,
            category="Транспорт",
        ),
        Transaction(
            date=datetime.date(2026, 1, 3),
            description="Бургер",
            amount=-600,
            category="Фастфуд",
        ),
        Transaction(
            date=datetime.date(2026, 1, 4),
            description="Зарплата",
            amount=100000,
            category="Зарплата",
        ),
    ]

    result = aggregate_by_category(txs)

    assert result["Транспорт"] == -550
    assert result["Фастфуд"] == -600
    assert result["Зарплата"] == 100000


def test_aggregate_empty():
    assert aggregate_by_category([]) == {}
