import io
import orm
from aiogram import Router, F
from aiogram import types
import numpy as np
from crawler import parse_api
from response_services import get_llm_response
from aiogram.filters import Command
import logging
from sql_parser import parse_sql
from sqlalchemy.ext.asyncio import AsyncSession

logging.basicConfig(level=logging.INFO)

router = Router()


def setup_router(router: Router,
                 bot,
                 session: AsyncSession,
                 openai_model: str | None = "gpt-3.5-turbo",
                 openrouter_model: str | None = "liquid/lfm-40b:free",
                 grok_model: str | None = 'grok-beta'):
    

    @router.message(Command("start"))
    async def start(message: types.Message):
        chat_user_id = message.from_user.id
        user = await orm.create_user(chat_user_id, session)
        await message.reply(
            f"Привет, {user}! Это твой апи строитель. Не забудь отправить .sql и url перед запросом",
            parse_mode="Markdown",
        )

    @router.message(Command("help"))
    async def start(message: types.Message):
        await message.reply(
            """Для отправки .sql необходимо ввести /sql перед отправкой.
            Для формирования базы датасета нужно отправить /docs и ссылку на апи""",
            parse_mode="Markdown",
        )
    
    @router.message(Command("sql"), F.document)
    async def handle_sql(message: types.Message):
        chat_user_id = message.from_user.id
        file_in_io = io.BytesIO()
        if not message.document.file_name.endswith(".sql"):
            await message.reply("Пожалуйста, отправьте файл с расширением `.sql`.")
            return
        
        file_info = await bot.get_file(message.document.file_id)
        await bot.download_file(file_info.file_path, destination=file_in_io)

        file_content = file_in_io.getvalue().decode("utf-8")

        content = parse_sql(file_content)
        await orm.add_sql(chat_user_id, content, session)
        await message.reply("SQL-файл успешно обработан!")

    @router.message(Command("docs"))
    async def handle_url(message: types.Message):
        chat_user_id = message.from_user.id
        url = message.text.strip()
        cleaned_url = url.replace('/docs ', '')
        url_text = await parse_api(cleaned_url)
        embedding = np.random.rand(1024)
        await orm.add_embeddings(chat_user_id, url_text, embedding, session)

        await message.reply(f"URL принят: {url}")

    @router.message()
    async def handle_query(message: types.Message):
        chat_user_id = message.from_user.id
        results = await orm.search_docs(message.text, session)
        response = "\n".join([f"{row['content']} (distance: {row['distance']})" for row in results])
        await message.reply(response if results else "Ничего не найдено.")
        sql = await orm.get_sql(chat_user_id, session)
        with open("../instruction.txt", "r") as file:
            instructions = file.read()
        result = instructions + message.text + response + str(sql.content)
        try:
            llm_response = await get_llm_response(result, openrouter_model, "openrouter")
            if llm_response is None:
                    llm_response = "Извините, не удалось получить ответ от модели."
            await message.answer(llm_response)
        except Exception as e:
            await message.answer(f"Произошла ошибка: {e}")


