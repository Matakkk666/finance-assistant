from collections import defaultdict

from src.models.transaction import Transaction


def aggregate_by_category(transactions: list[Transaction]) -> dict[str, float]:
    """Группирует транзакции по категориям и суммирует расходы/доходы."""
    result = defaultdict(float)

    for tx in transactions:
        # Если категория не задана, кидаем в "Без категории"
        cat = tx.category if tx.category else "Без категории"
        result[cat] += tx.amount

    return dict(result)
