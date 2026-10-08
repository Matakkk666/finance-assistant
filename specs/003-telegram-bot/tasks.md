# Задачи (Tasks) - Feature 003: Telegram Bot

- [ ] **Task 1: Зависимости и Аналитика**
  - Добавить `aiogram` в `requirements.txt` и установить.
  - Написать TDD тест для функции `aggregate_by_category` в `tests/test_analytics.py`.
  - Реализовать функцию в `src/services/analytics.py`.
- [ ] **Task 2: Каркас бота и Приватность**
  - Создать `src/bot/main.py` (инициализация бота).
  - Создать `src/bot/handlers.py` с базовой командой `/start` и проверкой на `OWNER_ID`.
- [ ] **Task 3: Интеграция всего конвейера**
  - Добавить хэндлер приема документов в бота.
  - Связать скачивание файла -> `parse_csv` -> `categorize_transactions` -> `aggregate_by_category` -> Отправка ответа.
- [ ] **Task 4: Ручной запуск**
  - Запустить бота локально и протестировать работу через Telegram.
