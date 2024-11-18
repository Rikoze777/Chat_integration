import io
from aiogram import Router, F
from aiogram import types
from aiogram.fsm.context import FSMContext
from crawler import parse_api
from response_services import get_llm_response
from aiogram.filters import Command
import logging
from aiogram.filters.state import State, StatesGroup
from sql_services import parse_sql

logging.basicConfig(level=logging.INFO)

router = Router()


def setup_router(router: Router,
                 bot,
                 openai_model: str | None = "gpt-3.5-turbo",
                 openrouter_model: str | None = "liquid/lfm-40b:free",
                 grok_model: str | None = 'grok-beta'):
    
    class FileUrlState(StatesGroup):
        waiting_for_file = State()
        waiting_for_url = State()
    
    @router.message(Command("start"))
    async def start(message: types.Message, state: FSMContext):
        await message.reply(
            "Привет! Отправьте файл с расширением `.sql`, затем URL для обработки.",
            parse_mode="Markdown",
        )
        await state.set_state(FileUrlState.waiting_for_file)
    
    @router.message(FileUrlState.waiting_for_file, F.document)
    async def handle_file(message: types.Message, state: FSMContext):
        file_in_io = io.BytesIO()
        if not message.document.file_name.endswith(".sql"):
            await message.reply("Пожалуйста, отправьте файл с расширением `.sql`.")
            return

        file_in_io = io.BytesIO()
        file_info = await bot.get_file(message.document.file_id)
        await bot.download_file(file_info.file_path, destination=file_in_io)

        file_content = file_in_io.getvalue().decode("utf-8")

        await state.update_data(file_content=file_content)
        await message.reply("Файл принят! Теперь отправьте URL.")
        await state.set_state(FileUrlState.waiting_for_url)
    
    @router.message(FileUrlState.waiting_for_url, F.text)
    async def handle_url(message: types.Message, state: FSMContext):
        url = message.text.strip()
        url_text = await parse_api(url)
        await state.update_data(url=url)

        data = await state.get_data()
        file_content = data.get("file_content")
        parsed_queries = parse_sql(file_content)

        with open("instruction.txt", "r") as file:
            instructions = file.read()
        result_query = instructions + url_text + parsed_queries

        await message.reply(f"URL принят: {url}")
        await message.reply(f"SQL-файл успешно обработан! Ожидайте")
        await message.answer("Запрос отправлен в модель OpenRouter. Пожалуйста, подождите...")
        try:
            llm_response = await get_llm_response(result_query, openrouter_model, "openrouter")
            if llm_response is None:
                    llm_response = "Извините, не удалось получить ответ от модели."
            await message.answer(llm_response)
        except Exception as e:
            await message.answer(f"Произошла ошибка: {e}")

        await state.clear()
