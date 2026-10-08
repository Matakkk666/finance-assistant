import csv
from datetime import datetime
from pathlib import Path
from src.models.transaction import Transaction


def parse_csv(file_path: Path | str) -> list[Transaction]:
    """Парсит CSV-файл и возвращает список объектов Transaction."""
    transactions = []
    with open(file_path, mode='r', encoding='utf-8') as file:
        # DictReader автоматически берет первую строку как ключи словаря
        reader = csv.DictReader(file)
        for row in reader:
            # 1. Преобразуем строку даты в объект date
            parsed_date = datetime.strptime(row['date'], '%Y-%m-%d').date()

            # 2. Преобразуем строку суммы в число (float), меняя запятую на
            # точку
            amount_str = row['amount'].replace(',', '.')
            amount_val = float(amount_str)

            # 3. Создаем модель транзакции
            tx = Transaction(
                date=parsed_date,
                description=row['description'],
                amount=amount_val
            )
            transactions.append(tx)

    return transactions
