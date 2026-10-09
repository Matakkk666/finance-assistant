# Задачи для Субагента (TDD)

Уважаемый субагент! Твоя задача — реализовать подключение БД строго по TDD.

- [ ] **Задача 1: Docker и Зависимости**
  - Создай `docker-compose.yml` в корне с сервисом `db` (образ `postgres:16-alpine`, порты `5432:5432`, задай POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB).
  - Добавь в `requirements.txt`: `sqlalchemy`, `asyncpg`, `alembic`, `greenlet`, `pytest-asyncio` (для асинхронных тестов).

- [ ] **Задача 2: Инициализация БД и Модели**
  - Создай `src/db/database.py` (настройка `create_async_engine` и `async_sessionmaker`).
  - Создай `src/models/db.py` и опиши декларативную модель `Transaction` (id, owner_id, date, amount, description, category).
  - Сгенерируй конфигурацию alembic (`alembic init -t async alembic`).
  - Настрой `alembic/env.py`, чтобы он видел нашу модель и брал URL из `.env`.
  - Сделай первую миграцию (revision) для создания таблицы транзакций.

- [ ] **Задача 3: Репозиторий (TDD)**
  - Напиши тест в `tests/test_db.py`, который использует асинхронную in-memory SQLite (или мок) и проверяет функцию `save_transactions`. Тест должен падать (Red).
  - Реализуй `save_transactions` в `src/db/repository.py` (Green).

- [ ] **Задача 4: Интеграция в пайплайн**
  - Измени код обработки документа (в `src/bot/handlers.py` или где он вызывается), чтобы после получения размеченных данных вызывалась функция `save_transactions`.
  - Проверь, что все линтеры (`flake8`) и тесты (`pytest`) проходят успешно.
