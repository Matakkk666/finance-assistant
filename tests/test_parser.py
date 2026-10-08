from pathlib import Path
from src.services.parser import parse_csv


def test_parse_csv():
    # Находим путь к нашему фейковому файлу
    file_path = Path(__file__).parent / "fixtures" / "sample.csv"

    # Пытаемся его распарсить
    transactions = parse_csv(file_path)

    # Проверяем, что вернулось 3 транзакции
    assert len(transactions) == 3

    # Проверяем первую транзакцию
    assert transactions[0].description == "Супермаркет"
    assert transactions[0].amount == -1500.50

    # Проверяем вторую транзакцию
    assert transactions[1].description == "Зарплата"
    assert transactions[1].amount == 50000.00

    # Проверяем третью транзакцию (с запятой в сумме)
    assert transactions[2].description == "Кофе"
    assert transactions[2].amount == -150.50
