from aiogram import Router
from aiogram import types
from services import get_llm_response, get_relevant_segment


router = Router()


def setup_router(router: Router, openai_model: str, openrouter_model: str, instructions: str, api_data_segments, api_index):
    @router.message(commands=["start"])
    async def start(message: types.Message):
        await message.answer("Привет! Я бот, который может использовать модели OpenAI и OpenRouter для написания API.")

    @router.message(commands=["openai"])
    async def handle_openai(message: types.Message):
        user_query = message.text
        await message.answer("Запрос отправлен в модель OpenAI. Пожалуйста, подождите...")

        try:
            relevant_api_data = get_relevant_segment(user_query, api_data_segments, api_index)
            llm_response = await get_llm_response(user_query, openai_model, instructions, relevant_api_data, "openai")
            await message.answer(llm_response)
        except Exception as e:
            await message.answer(f"Произошла ошибка: {e}")

    @router.message(commands=["openrouter"])
    async def handle_openrouter(message: types.Message):
        user_query = message.text
        await message.answer("Запрос отправлен в модель OpenRouter. Пожалуйста, подождите...")

        try:
            relevant_api_data = get_relevant_segment(user_query, api_data_segments, api_index)
            llm_response = await get_llm_response(user_query, openrouter_model, instructions, relevant_api_data, "openrouter")
            await message.answer(llm_response)
        except Exception as e:
            await message.answer(f"Произошла ошибка: {e}")
