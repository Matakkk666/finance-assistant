# План реализации: 007-bank-sync

## 1. Архитектура модулей и провайдеров
1. Создать пакет `src/services/bank/`:
   - `base.py`: интерфейс `BaseBankProvider` (абстрактный метод `fetch_transactions(since_date: date) -> list[Transaction]`).
   - `mock.py`: `MockBankProvider` (возвращает синтетические транзакции для тестов).
   - `tbank.py`: `TBankProvider` (клиент API Т-Банка).
   - `sber.py`: `SberProvider` (клиент API Сбера).
   - `mkb.py`: `MKBProvider` (клиент API МКБ).
   - `factory.py`: функция `get_bank_provider(name: str)` для создания нужного провайдера.

## 2. Логика сервиса синхронизации (BankSyncService)
2. Создать `src/services/bank/sync.py`:
   - Метод `sync_user_bank(owner_id: int, session: AsyncSession, provider: BaseBankProvider | None = None) -> dict`:
     - Запрашивает транзакции у провайдера за последние 30 дней.
     - Дедуплицирует транзакции: находит в базе транзакции пользователя и отфильтровывает уже существующие `(date, amount, description)`.
     - Если новых транзакций нет — возвращает статус `{new_count: 0, total_fetched: N}`.
     - Если новые есть:
       - Вызывает `categorize_transactions(new_transactions)` через LLM.
       - Сохраняет их в БД через `save_transactions(session, new_transactions, owner_id)`.
       - Формирует отчет по категориям (`aggregate_by_category`).
       - Возвращает `{new_count: len(new_transactions), categories: report_data}`.

## 3. Интеграция с Telegram-ботом
3. В `src/bot/handlers.py`:
   - Зарегистрировать команду `/sync` (с опциональным аргументом имени банка).
   - Проверять авторизацию (`owner_id`).
   - Показывать пользователю прогресс (`⏳ Подключаюсь к банку...`).
   - Выводить понятный структурированный результат.

## 4. Тестирование и верификация (TDD)
4. Написать unit- и интеграционные тесты:
   - `tests/test_bank_providers.py`: проверка провайдеров (`MockBankProvider`, `TBankProvider`, `SberProvider`, `MKBProvider` с мокированием `httpx`).
   - `tests/test_bank_sync.py`: проверка сервиса синхронизации (дедупликация, вызов LLM только для новых записей, запись в БД).
   - `tests/test_bot_sync.py`: проверка обработчика команды `/sync`.
   - Прогнать линтеры (`flake8`) и автотесты (`pytest`) через скилл `project-check`.
