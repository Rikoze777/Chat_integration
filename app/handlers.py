import io
import text_services
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
                 session: AsyncSession):
    
    async def process_request(model_name: str, message: types.Message, session: AsyncSession):
        chat_user_id = message.from_user.id
        user_query = message.text.strip().replace(f"/{model_name} ", "")
        docs = await orm.search_docs(user_query, chat_user_id, session)
        instructions = await orm.fetch_prompt(session, chat_user_id)
        
        prompt = f"Instrucrions: {instructions.content}" if instructions else ""
        docs_response = "\n".join(
            [f"{row['content']} (distance: {row['distance']})" for row in docs]
        ) if docs else ""
        
        sql = await orm.get_sql(chat_user_id, session)
        sql_doc = str(sql.content) if sql else ""
        full_input = user_query + docs_response + sql_doc
        
        try:
            llm_response = await get_llm_response(full_input, prompt, model_name)
            if not llm_response:
                llm_response = "Извините, не удалось получить ответ от модели."
            await message.answer(llm_response)
        except Exception as e:
            await message.answer(f"Произошла ошибка: {e}")

    @router.message(Command("start"))
    async def start(message: types.Message):
        chat_user_id = message.from_user.id
        user = await orm.create_user(chat_user_id, session)
        await message.reply(
            f"Привет, {user.tg_user_id}! Это твой ассистент. Не забудь просмотреть функционал в /help",
            parse_mode="Markdown",
        )

    @router.message(Command("help"))
    async def help(message: types.Message):
        await message.reply(
            """*Доступные команды:*
        
            📜 *Основные команды:*
            - `/start` — начать работу с ботом.
            - `/help` — показать справку.

            💾 *Работа с SQL:*
            - `/sql` — загрузите файл `.sql` и подпишите /sql.

            📚 *Работа с документами:*
            - `/docs [ссылка]` — отправьте ссылку на API, чтобы сформировать базу датасета.

            ✏️ *Добавление инструкций:*
            - `/prompt [текст]` — добавьте свои инструкции для обработки запросов.

            🤖 *Запросы к моделям:*
            - `/grok` — использовать модель *Grok*.
            - `/openrouter` — использовать модель *OpenRouter*.
            - `/openai` — использовать модель *OpenAI*.
            """,
            parse_mode="Markdown",
        )
    
    @router.message(Command("prompt"))
    async def handle_sql(message: types.Message):
        chat_user_id = message.from_user.id
        prompt =  message.text

        await orm.load_prompt(session, chat_user_id, prompt)
        await message.reply(
            """Ваши инструкции загружены""",
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
        
        chunk_size = 1024
        chunks = await text_services.split_into_chunks(url_text, chunk_size)
        embeddings = [np.random.rand(1024) for _ in chunks]
        
        await orm.add_chunks_to_db(chat_user_id, chunks, embeddings, session)
        await message.reply(f"URL принят: {url}")

    @router.message(Command("grok"))
    async def handle_grok(message: types.Message):
        await process_request("grok", message, session)

    @router.message(Command("openrouter"))
    async def handle_openrouter(message: types.Message):
        await process_request("openrouter", message, session)

    @router.message(Command("openai"))
    async def handle_openai(message: types.Message):
        await process_request("openai", message, session)
