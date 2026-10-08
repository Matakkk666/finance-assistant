# Задачи (Tasks) - Feature 002: Категоризация LLM

- [ ] **Task 1: Зависимости и Модель**
  - Добавить `google-generativeai` и `python-dotenv` в `requirements.txt`.
  - Обновить тест в `tests/models/test_transaction.py`, чтобы проверять пустое поле `category`.
  - Обновить `src/models/transaction.py` (добавить `category: str | None = None`).
- [ ] **Task 2: Подготовка промпта**
  - Написать тест на функцию-генератор промпта, убедиться, что она корректно склеивает транзакции в текст.
  - Написать саму функцию подготовки текста.
- [ ] **Task 3: LLM Сервис (Мок)**
  - Написать тест для `categorize_transactions`, замокав вызов Gemini (используя `unittest.mock.patch`).
  - Реализовать функцию `categorize_transactions` в `src/services/llm.py` (настройка ключа, вызов модели `gemini-2.5-flash`, парсинг ответа).
- [ ] **Task 4: Реальный тест (Опционально)**
  - Написать скрипт, который мы запустим один раз руками (вне `pytest`), чтобы убедиться, что реальный Gemini API работает и списывает копейки с баланса.
