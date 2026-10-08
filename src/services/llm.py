import json
from google import genai
from dotenv import load_dotenv

from src.models.transaction import Transaction

CATEGORIES = [
    "Самокаты", "Крипта", "Виза заграничная",
    "Хавка", "Фастфуд", "Рестораны",
    "Озон", "Веб3", "Переводы", "Прочее"
]


def build_prompt(transactions: list[Transaction]) -> str:
    """Генерирует текст промпта для ИИ на основе списка транзакций."""

    prompt = "Ты — финансовый ассистент. Твоя задача — категоризировать список транзакций.\n\n"
    prompt += "Категории: " + ", ".join(CATEGORIES) + "\n\n"
    prompt += "Верни JSON в формате: {\"<ID>\": \"<Категория>\"}.\n\n"
    prompt += "Транзакции:\n"

    for i, tx in enumerate(transactions):
        prompt += f"ID {i}: {tx.date} | {tx.description} | {tx.amount}\n"

    return prompt


# Загружаем переменные из .env (теперь os.environ увидит GEMINI_API_KEY)
load_dotenv()

# Создаем клиента (он сам возьмет GEMINI_API_KEY из окружения)
client = genai.Client()


def categorize_transactions(
        transactions: list[Transaction]) -> list[Transaction]:
    """Отправляет транзакции в Gemini и проставляет им категории."""
    if not transactions:
        return []

    prompt = build_prompt(transactions)

    # Отправляем запрос к Gemini
    response = client.models.generate_content(
        model='gemini-3.8-flash',
        contents=prompt
    )

    # Парсим JSON-ответ от нейросети
    try:
        # Иногда нейросеть оборачивает JSON в маркдаун блоки ```json ... ```,
        # счищаем это
        clean_text = response.text.replace(
            '```json', '').replace(
            '```', '').strip()
        result_map = json.loads(clean_text)

        # Проставляем категории обратно в объекты
        for i, tx in enumerate(transactions):
            # Если ИИ не вернул категорию для ID, ставим "Прочее"
            tx.category = result_map.get(str(i), "Прочее")

    except Exception as e:
        print(f"Ошибка парсинга ответа ИИ: {e}")

    return transactions
