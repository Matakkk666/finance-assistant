from src.services.llm import categorize_transactions
from src.models.transaction import Transaction
from datetime import date

def main():
    print("Создаем тестовые транзакции...")
    txs = [
        Transaction(date=date(2026, 10, 1), description="Оплата Yandex GO", amount=-500.0),
        Transaction(date=date(2026, 10, 2), description="Перевод от Ивана", amount=5000.0),
        Transaction(date=date(2026, 10, 3), description="Покупка крипты на Binance", amount=-10000.0)
    ]
    
    print("Отправляем запрос в реальный Gemini API...")
    result = categorize_transactions(txs)
    
    print("\nОтвет получен! Результат:")
    for tx in result:
        print(f"[{tx.category}] {tx.description} ({tx.amount})")

if __name__ == "__main__":
    main()
