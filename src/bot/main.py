import asyncio
import os
import sys

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from src.bot.handlers import router


async def main():
    load_dotenv()

    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        print("Ошибка: BOT_TOKEN не найден в .env")
        sys.exit(1)

    bot = Bot(token=bot_token)
    dp = Dispatcher()

    dp.include_router(router)

    print("🤖 Бот запущен! Нажмите Ctrl+C для остановки.")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nБот остановлен.")
