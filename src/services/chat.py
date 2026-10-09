import collections
from sqlalchemy import text
import re
from src.services.llm import client

_chat_history = {}


def get_chat_history(owner_id: int):
    if owner_id not in _chat_history:
        _chat_history[owner_id] = collections.deque(maxlen=6)
    return _chat_history[owner_id]


def validate_sql(sql: str) -> bool:
    """
    Проверяет SQL-запрос на наличие запрещенных команд.
    """
    forbidden_words = [
        "DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE"
    ]
    sql_upper = sql.upper()
    for word in forbidden_words:
        # Используем регулярное выражение для поиска слова целиком
        if re.search(rf'\b{word}\b', sql_upper):
            return False
    return True


def generate_sql(question: str, owner_id: int) -> str:
    """
    Генерирует SQL-запрос для PostgreSQL по вопросу пользователя.
    """
    history_text = ""
    history = _chat_history.get(owner_id, [])
    if history:
        history_lines = []
        for msg in history:
            role_str = "User" if msg["role"] == "user" else "Bot"
            history_lines.append(f"{role_str}: {msg['content']}")

        history_str = "\n".join(history_lines)
        history_text = f"История предыдущих сообщений:\n{history_str}\n\n"

    prompt = (
        "Ты эксперт по базам данных PostgreSQL. "
        "Твоя задача — перевести вопрос пользователя в валидный SQL-запрос.\n"
        "Схема таблицы:\n"
        "Таблица 'transactions'\n"
        "Колонки: id (INT), owner_id (INT), date (DATE), amount (FLOAT), "
        "description (VARCHAR), category (VARCHAR)\n\n"
        f"ОБЯЗАТЕЛЬНОЕ УСЛОВИЕ: Добавь фильтр по owner_id = {owner_id} "
        "в секцию WHERE каждого запроса.\n"
        "Возвращай ТОЛЬКО чистый SQL-запрос, без других слов, комментариев "
        "или форматирования markdown.\n\n"
        f"{history_text}"
        f"Вопрос пользователя: {question}"
    )

    response = client.models.generate_content(
        model='gemini-3.8-flash',
        contents=prompt
    )

    sql = response.text.replace('```sql', '').replace('```', '').strip()
    return sql


async def process_user_question(
        question: str,
        owner_id: int,
        db_session) -> str:
    """
    Основная логика Text-to-SQL.
    """
    sql = generate_sql(question, owner_id)

    if not validate_sql(sql):
        return "Извините, не могу выполнить этот запрос."

    try:
        # Выполняем SQL запрос
        result = await db_session.execute(text(sql))
        rows = result.fetchall()

        # Формируем промпт для генерации ответа
        prompt = (
            "Ты умный финансовый ассистент. Пользователь задал вопрос "
            "о своих финансах.\n"
            f"Вопрос пользователя: {question}\n\n"
            "Я выполнил SQL запрос к базе данных и получил следующий "
            "результат:\n"
            f"{rows}\n\n"
            "Сформулируй красивый, понятный и краткий ответ для человека "
            "на основе этих данных. Не упоминай SQL, базу данных "
            "или технические детали. Просто ответь на вопрос."
        )

        response = client.models.generate_content(
            model='gemini-3.8-flash',
            contents=prompt
        )

        final_answer = response.text.strip()

        # Сохраняем в историю
        history = get_chat_history(owner_id)
        history.append({"role": "user", "content": question})
        history.append({"role": "bot", "content": final_answer})

        return final_answer
    except Exception as e:
        return f"Произошла ошибка при выполнении запроса: {e}"
