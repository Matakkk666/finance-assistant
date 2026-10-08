from datetime import date

from src.models.transaction import Transaction


def test_create_transaction():
    """Тест проверяет, что модель транзакции корректно создается."""
    tx = Transaction(
        date=date(2026, 10, 8),
        description="Покупка самоката",
        amount=-1500.50
    )

    assert tx.date == date(2026, 10, 8)
    assert tx.description == "Покупка самоката"
    assert tx.amount == -1500.50
    assert tx.category is None
