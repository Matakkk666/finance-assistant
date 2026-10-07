# Архитектура проекта

## 1. Компоненты системы
- **Telegram-клиент**: Интерфейс взаимодействия с пользователем (чат и кнопка Mini App).
- **Бот-сервис (aiogram 3)**: Отвечает за прием сообщений, файлов выписок и маршрутизацию команд.
- **Web API (FastAPI)**: Служит бэкендом для Mini App (отдает данные для графиков) и объединяет логику.
- **LLM API (Gemini/GPT)**: Внешний сервис для автоматической категоризации транзакций и генерации ответов.
- **База данных (PostgreSQL)**: Хранит пользователей, историю загрузок и сами транзакции.

## 2. Диаграмма архитектуры (High-level)

```mermaid
flowchart TD
    User([Пользователь]) -->|Текст, Файлы выписок| TgBot[Telegram Bot]
    User -->|Открывает дашборд| WebApp[Telegram Mini App]
    
    TgBot <-->|aiogram API| AppServer[App Server / FastAPI]
    WebApp <-->|REST API| AppServer
    
    AppServer <-->|SQLAlchemy ORM| DB[(PostgreSQL)]
    AppServer <-->|API Requests| LLM[Gemini / GPT API]
```

## 3. Модель данных (ER-диаграмма)

```mermaid
erDiagram
    USER ||--o{ UPLOAD_SESSION : creates
    USER ||--o{ TRANSACTION : owns
    UPLOAD_SESSION ||--o{ TRANSACTION : contains
    
    USER {
        int id PK
        int telegram_id
        string username
        datetime created_at
    }
    
    UPLOAD_SESSION {
        int id PK
        int user_id FK
        string filename
        datetime uploaded_at
        string status "pending | processing | done | error"
    }
    
    TRANSACTION {
        int id PK
        int user_id FK
        int session_id FK
        date transaction_date
        string description
        float amount
        string category
        boolean is_processed "Флаг, прошла ли транзакция через LLM"
    }
```

## 4. Общий алгоритм обработки файла (Data Flow)
1. Пользователь скидывает `.csv` файл в бота.
2. Бот скачивает файл, создает запись `UPLOAD_SESSION` со статусом `pending`.
3. Парсер читает CSV и сохраняет сырые `TRANSACTION` (категория пустая, `is_processed=False`).
4. Сервис берет пачку неразмеченных транзакций и отправляет единым JSON-запросом в LLM API с промптом категорий.
5. LLM возвращает размеченный JSON (каждой транзакции присвоена категория).
6. База данных обновляется, `is_processed=True`, статус сессии `done`.
7. Пользователь получает уведомление в Telegram: "Файл успешно обработан".
