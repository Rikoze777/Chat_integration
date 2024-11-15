from aiogram import Router
from aiogram import types
from services import get_llm_response
from aiogram.filters import Command
import logging


logging.basicConfig(level=logging.INFO)

router = Router()


def setup_router(router: Router,
                 instructions: str,
                 api_data_segments,
                 api_index,
                 openai_model: str | None = "gpt-3.5-turbo",
                 openrouter_model: str | None = "liquid/lfm-40b:free",
                 grok_model: str | None = 'grok-beta',):
    @router.message(Command("start"))
    async def start(message: types.Message):
        await message.answer("Привет! Я бот, который может использовать модели OpenAI и OpenRouter для написания API.")

    @router.message(Command("openai"))
    async def handle_openai(message: types.Message):
        user_query = message.text
        await message.answer("Запрос отправлен в модель OpenAI. Пожалуйста, подождите...")

        try:
            relevant_api_data = get_relevant_segment(user_query, api_data_segments, api_index)
            llm_response = await get_llm_response(user_query, openai_model, instructions, relevant_api_data, "openai")
            
            if llm_response is None:
                llm_response = "Извините, не удалось получить ответ от модели."
            
            await message.answer(llm_response)
        except Exception as e:
            await message.answer(f"Произошла ошибка: {e}")

    @router.message(Command("openrouter"))
    async def handle_openrouter(message: types.Message):
        user_query = message.text
        await message.answer("Запрос отправлен в модель OpenRouter. Пожалуйста, подождите...")

        try:
            relevant_api_data = get_relevant_segment(user_query, api_data_segments, api_index)
            llm_response = await get_llm_response(user_query, openrouter_model, instructions, relevant_api_data, "openrouter")
            
            if llm_response is None:
                llm_response = f"Извините, не удалось получить ответ от модели."
            
            await message.answer(llm_response)
        except Exception as e:
            await message.answer(f"Произошла ошибка: {e}")

    @router.message(Command("grok"))
    async def handle_grok(message: types.Message):
        user_query = message.text
        await message.answer("Запрос отправлен в модель GROK. Пожалуйста, подождите...")

        try:
            relevant_api_data = get_relevant_segment(user_query, api_data_segments, api_index)
            llm_response = await get_llm_response(user_query, grok_model, instructions, relevant_api_data, "grok")
            
            if llm_response is None:
                llm_response = f"Извините, не удалось получить ответ от модели."
            
            await message.answer(llm_response)
        except Exception as e:
            await message.answer(f"Произошла ошибка: {e}")