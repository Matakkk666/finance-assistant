# Задачи для Субагента Frontend

Твоя задача — создать красивое Telegram Mini App на React. У тебя в системе доступен `npm` и `node`.

- [ ] **Задача 1: Инициализация проекта**
  - В корне проекта выполни: `npm create vite@latest frontend -- --template react-ts`.
  - Перейди в `frontend/` и выполни `npm install`.
  - Установи зависимости: `npm install tailwindcss postcss autoprefixer recharts axios @twa-dev/sdk`.
  - Инициализируй Tailwind (`npx tailwindcss init -p`) и настрой `tailwind.config.js`.

- [ ] **Задача 2: Telegram SDK и Стили**
  - В `src/main.tsx` инициализируй WebApp (`WebApp.ready()`).
  - В Tailwind настрой использование CSS переменных Telegram (например, `var(--tg-theme-bg-color)`) для поддержки темной/светлой темы.

- [ ] **Задача 3: Верстка дашборда (App.tsx)**
  - Получи `user.id` из `WebApp.initDataUnsafe` (или замокай `123` для браузера).
  - Сделай запрос через `axios` к `http://127.0.0.1:8000/api/stats` и `/api/transactions`.
  - Отрисуй сверху общую сумму трат.
  - Ниже отрисуй `PieChart` из `recharts` с распределением по категориям.
  - Снизу отрисуй список транзакций. Добавь вибрацию `WebApp.HapticFeedback.impactOccurred('light')` при клике на элемент списка.

- [ ] **Задача 4: Проверка сборки**
  - Выполни `npm run build` в папке `frontend`. Убедись, что появилась папка `dist`, которую сможет раздавать Backend.
  - Напиши отчет по завершении работы.
