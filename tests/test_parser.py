from pathlib import Path
from datetime import date
from src.services.parser import parse_csv


def test_parse_csv_semicolon():
    file_path = Path(__file__).parent / "fixtures" / "tinkoff_test1.csv"
    transactions = parse_csv(file_path)

    assert len(transactions) == 2

    assert transactions[0].description == "Магнит"
    assert transactions[0].amount == -109.99
    assert transactions[0].date == date(2026, 10, 7)

    assert transactions[1].description == "Анна К."
    assert transactions[1].amount == 1500.00
    assert transactions[1].date == date(2026, 10, 4)


def test_parse_csv_comma():
    file_path = Path(__file__).parent / "fixtures" / "tinkoff_test2.csv"
    transactions = parse_csv(file_path)

    assert len(transactions) == 2

    assert transactions[0].description == "Магнит"
    assert transactions[0].amount == -109.99
    assert transactions[0].date == date(2026, 10, 7)

    assert transactions[1].description == "Анна К."
    assert transactions[1].amount == 1500.00
    assert transactions[1].date == date(2026, 10, 4)
