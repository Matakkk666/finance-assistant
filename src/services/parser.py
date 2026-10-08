import pandas as pd

from pathlib import Path

from src.models.transaction import Transaction


def parse_csv(file_path: Path | str) -> list[Transaction]:
    """Парсит CSV/Excel-файл и возвращает список объектов Transaction."""
    file_path = str(file_path)

    if file_path.endswith(('.xlsx', '.xls')):
        df = pd.read_excel(file_path)
    else:
        # Пытаемся прочитать с разделителем ;
        df = pd.read_csv(file_path, sep=';', encoding='utf-8')
        if len(df.columns) <= 1:
            # Если колонок мало, возможно разделитель ,
            df = pd.read_csv(file_path, sep=',', encoding='utf-8')

    df.columns = df.columns.str.strip()

    transactions = []

    # Определяем нужные колонки
    date_col = 'Дата операции' if 'Дата операции' in df.columns else 'date'
    amount_col = (
        'Сумма операции' if 'Сумма операции' in df.columns else 'amount'
    )
    desc_col = 'Описание' if 'Описание' in df.columns else 'description'

    for _, row in df.iterrows():
        try:
            raw_date = row[date_col]
            raw_amount = row[amount_col]
            desc = row[desc_col]

            # Пропускаем пустые строки
            if pd.isna(raw_date) or pd.isna(raw_amount):
                continue

            if isinstance(raw_date, str):
                try:
                    parsed_date = pd.to_datetime(
                        raw_date, format='%d.%m.%Y %H:%M:%S'
                    ).date()
                except ValueError:
                    parsed_date = pd.to_datetime(raw_date).date()
            else:
                parsed_date = pd.to_datetime(raw_date).date()

            # Парсинг суммы
            if isinstance(raw_amount, str):
                amount_str = raw_amount.replace(',', '.').replace(' ', '')
                amount_val = float(amount_str)
            else:
                amount_val = float(raw_amount)

            tx = Transaction(
                date=parsed_date,
                description=str(desc).strip(),
                amount=amount_val
            )
            transactions.append(tx)
        except Exception:
            continue

    return transactions
