# План реализации (Telegram Mini App)

1. **Инициализация Frontend:** Создать проект React + Vite + TS в папке `frontend/`. Установить Tailwind, Recharts, `axios` и `@twa-dev/sdk`.
2. **Backend API:** В `src/api/` создать эндпоинты `GET /api/stats` и `GET /api/transactions`.
3. **Обновление Бота:** В `src/bot/handlers.py` добавить кнопку (ReplyKeyboardMarkup или InlineKeyboardMarkup) с типом `web_app`, которая открывает наш дашборд (пока можно указывать ngrok URL или localhost для тестов).
4. **Сборка Frontend (UI):** Написать React-компоненты:
   - `Header` (Отображает имя пользователя и баланс).
   - `Chart` (Recharts Donut chart с категориями).
   - `TransactionList` (список транзакций).
5. **Интеграция Frontend + Backend:** Настроить `axios` на фронте для запросов к FastAPI.
6. **Настройка раздачи статики:** Настроить FastAPI (в `src/main.py`) так, чтобы он раздавал папку `frontend/dist/` как статические файлы для продакшена.
