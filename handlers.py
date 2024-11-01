from aiogram import Router
from aiogram.filters import Command
from environs import Env
from aiogram import types
from keyboard import markup
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from llama_index import GPTIndex


router = Router()

user_data = {}

env = Env()
env.read_env()
TELEGRAM_TOKEN = env.str("TELEGRAM_TOKEN")
OPENAI_API_KEY = env.str("OPENAI_API_KEY")

INSTRUCTION_FILE = 'instruction.txt'


def load_instruction():
    with open(INSTRUCTION_FILE, 'r') as file:
        return file.read()


@router.message(Command('start'))
async def send_welcome(message: types.Message):
    await message.reply("Привет! Отправь свой запрос, и я передам его в модель.")


@router.message()
async def handle_message(message: types.Message):
    instruction = load_instruction()
    user_query = message.text
    
    rag_model = GPTIndex(openai_api_key=OPENAI_API_KEY, instruction=instruction)
    
    response = rag_model.get_response(user_query)
    await message.reply(response)