import os

from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.types import Message

from src.services.analytics import aggregate_by_category
from src.services.llm import categorize_transactions
from src.services.parser import parse_csv

router = Router()


def get_owner_id() -> int:
    owner = os.getenv("OWNER_ID")
    return int(owner) if owner else 0


@router.message(Command("start"))
async def cmd_start(message: Message):
    owner_id = get_owner_id()
    if owner_id and message.from_user.id != owner_id:
        await message.answer("Извините, это приватный бот.")
        return

    await message.answer(
        "Привет! Отправь мне CSV файл с выпиской, и я его проанализирую."
    )


@router.message(F.document)
async def handle_document(message: Message, bot: Bot):
    owner_id = get_owner_id()
    if owner_id and message.from_user.id != owner_id:
        return

    if not message.document.file_name.endswith(('.csv', '.xlsx', '.xls')):
        await message.answer("Пожалуйста, отправьте CSV или Excel файл.")
        return

    status_msg = await message.answer("⏳ Файл получен. Начинаю анализ...")

    # 1. Скачивание файла
    os.makedirs("data/tmp", exist_ok=True)
    local_path = f"data/tmp/{message.document.file_name}"

    try:
        file_id = message.document.file_id
        file = await bot.get_file(file_id)
        await bot.download_file(file.file_path, local_path)

        # 2. Парсинг
        await status_msg.edit_text("⏳ Парсинг транзакций...")
        transactions = parse_csv(local_path)

        # 3. Категоризация ИИ
        await status_msg.edit_text(
            "🧠 Отправляю данные в нейросеть (Gemini)..."
        )
        transactions = categorize_transactions(transactions)

        from src.db.database import async_session
        from src.db.repository import save_transactions
        await status_msg.edit_text("💾 Сохраняю транзакции в базу данных...")
        async with async_session() as session:
            await save_transactions(
                session, transactions, message.from_user.id
            )

        # 4. Аналитика
        await status_msg.edit_text("📊 Подвожу итоги...")
        report_data = aggregate_by_category(transactions)

        # 5. Формирование ответа
        if not report_data:
            await status_msg.edit_text(
                "Транзакций не найдено или произошла ошибка."
            )
            return

        report_text = "📊 <b>Отчет по категориям:</b>\n\n"
        for cat, amount in report_data.items():
            report_text += f"• <b>{cat}</b>: {amount:.2f}\n"

        await status_msg.edit_text(report_text, parse_mode="HTML")

    except Exception as e:
        await status_msg.edit_text(f"❌ Произошла ошибка при обработке:\n{e}")
    finally:
        if os.path.exists(local_path):
            os.remove(local_path)
