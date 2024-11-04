import asyncio
import handlers
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from environs import Env
from aiogram.types import Router

import services


async def main():
    env = Env()
    env.read_env()
    TELEGRAM_TOKEN = env.str("TELEGRAM_TOKEN")
    openai_model = env.str("GPT_MODEL", "gpt-3.5-turbo")
    openrouter_model = env.str("OPENROUTER_MODEL", "liquid/lfm-40b:free")

    bot = Bot(token=TELEGRAM_TOKEN)
    dp = Dispatcher(bot)
    router = Router()


    with open("instructions.txt", "r", encoding="utf-8") as file:
        instructions = file.read()


    api_data_segments, api_index = services.load_and_index_api_data()


    handlers.setup_router(router, openai_model, openrouter_model, instructions, api_data_segments, api_index)
    dp.include_router(router)

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())