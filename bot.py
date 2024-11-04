import asyncio
import handlers
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from environs import Env


async def main():
    env = Env()
    env.read_env()
    TELEGRAM_TOKEN = env.str("TELEGRAM_TOKEN")

    bot = Bot(token=TELEGRAM_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(bot=bot, storage=storage)
    dp.include_routers(handlers.router)

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())