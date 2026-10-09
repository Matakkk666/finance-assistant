# План реализации (БД и SQLAlchemy)

1. **Инфраструктура Docker:** Создать `docker-compose.yml`, который поднимает контейнер с PostgreSQL. Это позволит разработчику локально иметь рабочую БД.
2. **Зависимости:** Добавить `sqlalchemy`, `asyncpg`, `alembic` в `requirements.txt`.
3. **Настройка Alembic:** Инициализировать alembic (папка `alembic/` и `alembic.ini`).
4. **Слой данных (Models):** Создать SQLAlchemy модель `TransactionDB` в `src/models/db.py`, которая будет соответствовать нашей Pydantic/Dataclass модели.
5. **Подключение (Session):** Настроить фабрику сессий в `src/db/database.py`, которая читает URL базы из переменных окружения (`.env`).
6. **Репозиторий (CRUD):** Создать файл `src/db/repository.py` с функцией для пакетного сохранения транзакций (bulk insert). **Обязательно написать тесты с использованием тестовой in-memory БД (SQLite) или моков.**
7. **Интеграция:** Обновить пайплайн в `src/bot/handlers.py` (или `analytics.py`), чтобы после разметки LLM транзакции отправлялись в базу.
