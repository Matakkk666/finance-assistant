# Задачи для реализации: 007-bank-sync (TDD)

Каждая задача выполняется строго по методологии TDD: **Red (пишем падающий тест)** ➡️ **Green (минимальный рабочий код)** ➡️ **Refactor (чистим код и проверяем линтером)**.

---

### Задача 1: Базовый интерфейс и MockBankProvider
- [x] Написать тест в `tests/test_bank_providers.py`:
  - Проверить, что `MockBankProvider.fetch_transactions(since_date)` возвращает список объектов `Transaction` с корректными полями (`date`, `amount`, `description`).
  - Убедиться, что тест **падает** (Red).
- [x] Реализовать интерфейс и мок-провайдер:
  - Создать `src/services/bank/__init__.py`.
  - В `src/services/bank/base.py` объявить `BaseBankProvider` с абстрактным методом `fetch_transactions(self, since_date: datetime.date) -> list[Transaction]`.
  - В `src/services/bank/mock.py` реализовать `MockBankProvider(BaseBankProvider)`.
  - Запустить тест, убедиться, что он стал **зеленым** (Green).

---

### Задача 2: Провайдеры Сбер, Т-Банк, МКБ и Фабрика провайдеров
- [x] Написать тесты в `tests/test_bank_providers.py`:
  - Замокать `httpx.AsyncClient` для `TBankProvider`, `SberProvider`, `MKBProvider` (имитация ответов банковских API с транзакциями).
  - Проверить парсинг ответов каждого банка в унифицированный `list[Transaction]`.
  - Проверить фабрику `get_bank_provider(name)`: создание провайдеров по именам `"mock"`, `"tbank"`, `"sber"`, `"mkb"`.
  - Убедиться, что тесты **падают** (Red).
- [x] Реализовать провайдеры и фабрику:
  - Создать `src/services/bank/tbank.py`.
  - Создать `src/services/bank/sber.py`.
  - Создать `src/services/bank/mkb.py`.
  - Создать `src/services/bank/factory.py` с функцией `get_bank_provider(name: str = "mock")`.
  - Убедиться, что тесты стали **зелеными** (Green).

---

### Задача 3: Сервис синхронизации и Дедупликация (BankSyncService)
- [x] Написать тесты в `tests/test_bank_sync.py`:
  - Тест дедупликации: если транзакции уже есть в БД для данного `owner_id`, сервис не должен вызывать LLM и не должен повторно сохранять их в БД.
  - Тест синхронизации новых трат: если есть новые транзакции, сервис вызывает `categorize_transactions` (замоканный) только для новых записей и сохраняет их через `save_transactions`.
  - Убедиться, что тесты **падают** (Red).
- [x] Реализовать сервис:
  - В `src/services/bank/sync.py` реализовать функцию `sync_user_bank(owner_id: int, session: AsyncSession, provider: BaseBankProvider | None = None) -> dict`.
  - Убедиться, что тесты стали **зелеными** (Green).

---

### Задача 4: Интеграция в Telegram-бот (/sync) и верификация проекта
- [x] В `tests/test_bot_sync.py` написать тесты на команду `/sync` (с проверкой прав `owner_id` и вызова `sync_user_bank`).
- [x] В `src/bot/handlers.py` зарегистрировать хэндлер на команду `Command("sync")`.
  - Поддержка параметров (например, `/sync tbank` или просто `/sync`).
  - Вызов `sync_user_bank(...)`.
  - Отправка понятного отчета пользователю.
- [x] Прогнать скилл `project-check` (линтер `flake8` и тесты `pytest`).
