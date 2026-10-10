---
name: add-new-bank
description: Используй этот скилл, когда пользователь просит добавить новый банк или банковский провайдер (например, ВТБ, Альфа-Банк, Райффайзен, Monobank и др.) для онлайн-синхронизации.
---

# Добавление нового банковского провайдера

Этот скилл пошагово описывает добавление поддержки нового онлайн-банка в систему синхронизации транзакций.

## Пошаговый процесс

### Шаг 1. Определение параметров банка
Выясни (из запроса пользователя или документации API банка):
- Технический идентификатор банка в нижнем регистре (например: `vtb`, `alfa`, `raiffeisen`, `monobank`).
- Название класса провайдера (например: `VTBProvider`, `AlfaProvider`).
- Переменную окружения для API-токена (например: `VTB_API_TOKEN`, `ALFA_API_TOKEN`).
- Формат ответа API банка и структуру полей (где дата, сумма и описание транзакции).

---

### Шаг 2. Создание файла провайдера
Создай файл `src/services/bank/<bank_id>.py`:
- Унаследуй класс от `BaseBankProvider` (из `src.services.bank.base`).
- Реализуй асинхронный метод `fetch_transactions(self, since_date: datetime.date) -> list[Transaction]`.
- Используй `httpx.AsyncClient` для выполнения HTTP-запроса к API банка.
- Передавай токен авторизации из `os.getenv("<BANK_ID>_API_TOKEN")` в заголовках (`Authorization` / `X-Token`).
- Преобразуй полученный JSON в список объектов `Transaction(date=..., description=..., amount=...)`.
- Обрабатывай сетевые ошибки и статус-коды (возвращай пустой список `[]` или понятную ошибку).

Пример структуры:
```python
import datetime
import os
import httpx
from src.services.bank.base import BaseBankProvider
from src.models.transaction import Transaction


class AlfaProvider(BaseBankProvider):
    async def fetch_transactions(
        self, since_date: datetime.date
    ) -> list[Transaction]:
        token = os.getenv("ALFA_API_TOKEN", "")
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.alfabank.ru/v1/statement",
                params={"from": since_date.isoformat()},
                headers=headers,
            )
            if response.status_code == 200:
                data = response.json()
                return [
                    Transaction(
                        date=datetime.date.fromisoformat(item["date"]),
                        description=item["description"],
                        amount=float(item["amount"]),
                    )
                    for item in data.get("transactions", [])
                ]
            return []
```

---

### Шаг 3. Регистрация в фабрике провайдеров
Открой `src/services/bank/factory.py`:
1. Импортируй созданный класс провайдера:
   ```python
   from src.services.bank.<bank_id> import <BankName>Provider
   ```
2. Добавь банк в словарь `providers`:
   ```python
   providers = {
       "mock": MockBankProvider,
       "sber": SberProvider,
       "tbank": TBankProvider,
       "mkb": MKBProvider,
       "<bank_id>": <BankName>Provider,
   }
   ```

---

### Шаг 4. Написание автотестов (TDD)
Открой `tests/test_bank_providers.py`:
1. Добавь асинхронный тест для нового провайдера с мокированием `httpx.AsyncClient.get`:
   ```python
   @pytest.mark.asyncio
   async def test_<bank_id>_provider():
       with patch("httpx.AsyncClient.get") as mock_get:
           mock_response = AsyncMock()
           mock_response.status_code = 200
           mock_response.json = lambda: {
               "transactions": [
                   {"date": "2026-10-10", "description": "Покупка", "amount": -500.0}
               ]
           }
           mock_get.return_value = mock_response

           provider = <BankName>Provider()
           txs = await provider.fetch_transactions(datetime.date.today())
           assert len(txs) == 1
           assert txs[0].description == "Покупка"
   ```
2. В `test_get_bank_provider` добавь проверку фабрики:
   ```python
   assert isinstance(get_bank_provider("<bank_id>"), <BankName>Provider)
   ```

---

### Шаг 5. Проверка качества кода
Запусти проверки:
```bash
python -m flake8 src tests
python -m pytest tests/test_bank_providers.py
```
Убедись, что нет нарушений PEP8 и все тесты зеленые.

---

### Шаг 6. Инструкция для пользователя
После добавления провайдера сообщи пользователю:
1. Какую переменную окружения нужно прописать в `.env` (например, `ALFA_API_TOKEN="твой_токен"`).
2. Как запустить синхронизацию в Telegram-боте:
   - `/sync <bank_id>` (например, `/sync alfa`).
