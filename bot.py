import asyncio
import handlers
import services
from aiogram import Bot, Dispatcher
from environs import Env
from aiogram import Router

env = Env()
env.read_env()
TELEGRAM_TOKEN = env.str("TELEGRAM_TOKEN")
OPENAI_MODEL = env.str("GPT_MODEL", "gpt-3.5-turbo")
OPENROUTER_MODEL = env.str("OPENROUTER_MODEL", "liquid/lfm-40b:free")
GROK_MODEL = env.str("GROK_MODEL", "grok-beta")


async def main():
    bot = Bot(token=TELEGRAM_TOKEN)
    dp = Dispatcher()
    router = Router()

    with open("instruction.txt", "r") as file:
        instructions = file.read()

    api_data_segments, api_index = services.load_and_index_api_data()

    handlers.setup_router(router, OPENAI_MODEL, OPENROUTER_MODEL, GROK_MODEL, instructions, api_data_segments, api_index)
    dp.include_router(router)

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())