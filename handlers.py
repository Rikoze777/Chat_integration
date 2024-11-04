from aiogram import Router
from aiogram.filters import Command
from environs import Env
from aiogram import types
import openai
from sentence_transformers import SentenceTransformer

from services import get_llm_response
import services


router = Router()

user_data = {}

env = Env()
env.read_env()

OPENAI_API_KEY = env.str("OPENAI_API_KEY")
GPT_MODEL = env.str("GPT_MODEL")


with open("instructions.txt", "r", encoding="utf-8") as file:
        instructions = file.read()


with open("api_data.txt", "r", encoding="utf-8") as file:
    api_data = file.read()


openai.api_key = OPENAI_API_KEY
model = SentenceTransformer('sentence-transformers/paraphrase-MiniLM-L6-v2')
api_data_segments, api_index, api_embeddings = services.load_and_index_api_data()


@router.message(Command('start'))
async def send_welcome(message: types.Message):
    await message.reply("Привет! Отправь свой запрос, и я передам его в модель.")


@router.message()
async def handle_message(message: types.Message):
    user_query = message.text
    await message.answer("Запрос отправлен в LLM. Пожалуйста, подождите...")

    try:
        llm_response = await get_llm_response(user_query, model, instructions, api_index, api_data_segments)
        await message.answer(llm_response)
    except Exception as e:
        await message.answer(f"Произошла ошибка: {e}")
