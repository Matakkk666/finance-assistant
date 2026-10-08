from unittest.mock import patch
from src.services.llm import categorize_transactions
import datetime

from src.models.transaction import Transaction
from src.services.llm import build_prompt


def test_build_prompt():
    txs = [
        Transaction(
            date=datetime.date(
                2026,
                10,
                1),
            description="Супермаркет",
            amount=-1500.50),
        Transaction(
            date=datetime.date(
                2026,
                10,
                2),
            description="Зарплата",
            amount=50000.00)]

    prompt = build_prompt(txs)

    # Проверяем, что промпт содержит нужные данные
    assert "ID 0: 2026-10-01 | Супермаркет | -1500.5" in prompt
    assert "ID 1: 2026-10-02 | Зарплата | 50000.0" in prompt

    # Проверяем, что в промпте есть инструкции для ИИ
    assert "Категории:" in prompt
    assert "Верни JSON" in prompt


@patch('src.services.llm.client.models.generate_content')
def test_categorize_transactions(mock_generate):
    # 1. Настраиваем фейковый ответ от нейросети
    class MockResponse:
        text = '{"0": "Хавка", "1": "Прочее"}'

    mock_generate.return_value = MockResponse()

    # 2. Подготавливаем тестовые данные
    txs = [
        Transaction(
            date=datetime.date(
                2026,
                10,
                1),
            description="Супермаркет",
            amount=-1500.50),
        Transaction(
            date=datetime.date(
                2026,
                10,
                2),
            description="Зарплата",
            amount=50000.00)]

    # 3. Вызываем функцию (она не пойдет в интернет, а обратится к нашему
    # mock_generate)
    categorized_txs = categorize_transactions(txs)

    # 4. Проверяем результаты
    assert len(categorized_txs) == 2
    assert categorized_txs[0].category == "Хавка"
    assert categorized_txs[1].category == "Прочее"
