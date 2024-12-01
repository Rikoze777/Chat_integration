import asyncio
import handlers
from aiogram import Bot, Dispatcher
from environs import Env
from aiogram import Router
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session

env = Env()
env.read_env()
TELEGRAM_TOKEN = env.str("TELEGRAM_TOKEN")
OPENAI_MODEL = env.str("GPT_MODEL", "gpt-3.5-turbo")
OPENROUTER_MODEL = env.str("OPENROUTER_MODEL", "liquid/lfm-40b:free")
GROK_MODEL = env.str("GROK_MODEL", "grok-beta")
HUGGINGFACE_TOKEN = env.str("HUGGINGFACE_TOKEN")


async def main():
    bot = Bot(token=TELEGRAM_TOKEN)
    dp = Dispatcher()
    router = Router()

    async for session in get_session():
        handlers.setup_router(router, bot, session)
    dp.include_router(router)

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())