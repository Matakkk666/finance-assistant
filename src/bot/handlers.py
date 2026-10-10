from src.services.bank.factory import get_bank_provider
from src.services.bank.sync import sync_user_bank
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    WebAppInfo,
)
from src.services.chat import process_user_question  # noqa
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

    if not message.document.file_name.endswith((".csv", ".xlsx", ".xls")):
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


@router.message(Command("app"))
async def cmd_app(message: Message):
    owner_id = get_owner_id()
    if owner_id and message.from_user.id != owner_id:
        return

    webapp_url = os.getenv("WEBAPP_URL", "https://hot-parrots-tie.loca.lt/")
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Открыть Дашборд", web_app=WebAppInfo(url=webapp_url)
                )
            ]
        ]
    )
    await message.answer(
        "Нажмите кнопку ниже, чтобы открыть дашборд:", reply_markup=keyboard
    )


@router.message(Command("sync"))
async def cmd_sync(message: Message):
    owner_id = get_owner_id()
    if owner_id and message.from_user.id != owner_id:
        return

    status_msg = await message.answer("Синхронизация с банком...")

    parts = message.text.split(maxsplit=1)
    bank_name = parts[1] if len(parts) > 1 else "mock"

    try:
        provider = get_bank_provider(bank_name)
    except ValueError:
        from src.services.bank.factory import providers
        available = ", ".join(providers.keys())
        await status_msg.edit_text(
            f"Неизвестный банк: {bank_name}. Доступны: {available}."
        )
        return

    try:
        from src.db.database import async_session

        async with async_session() as session:
            report = await sync_user_bank(
                message.from_user.id, session, provider
            )

        report_text = (
            f"Синхронизация успешна\n\n"
            f"Получено: {report['fetched']}\n"
            f"Новых: {report['new']}\n\n"
        )
        if report["categories"]:
            report_text += "Категории новых транзакций:\n"
            for cat, count in report["categories"].items():
                report_text += f"• {cat}: {count}\n"

        await status_msg.edit_text(report_text, parse_mode="HTML")
    except Exception as e:
        await status_msg.edit_text(f"Ошибка синхронизации:\n{e}")


@router.message(F.text)
async def handle_text_message(message: Message):
    owner_id = get_owner_id()
    if owner_id and message.from_user.id != owner_id:
        return

    status_msg = await message.answer("🧠 Думаю...")

    from src.db.database import async_session

    try:
        async with async_session() as session:
            answer = await process_user_question(
                message.text, message.from_user.id, session
            )
            await status_msg.edit_text(answer)
    except Exception as e:
        await status_msg.edit_text(f"❌ Ошибка:\n{e}")
