import os

from dotenv import load_dotenv
from pathlib import Path


from pyrogram import Client, enums
from pyrogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

from database.MongoDBConnection import MongoDBConnection
from database.user_repository import UserRepository

env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(env_path)

BOT_USERNAME = os.getenv('BOT_USERNAME')

db = MongoDBConnection()
user_repository = UserRepository(db, 'users')


async def handle_start_command(client: Client, message: Message):
    user_id = message.from_user.id
    user = user_repository.get_user_by_id(user_id)
    if user is not None and user.get("phone_number") is None:
        keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton("Отправить контакт ☎️", request_contact=True)]], one_time_keyboard=True, resize_keyboard=True)
        await message.reply_text(text="🕵️‍♂ Привет! Чтобы узнать о возможностях бота — зергистрируйся.\n\nПришли мне свой номер телефона нажав на кнопку ниже:", reply_markup=keyboard, parse_mode=enums.ParseMode.HTML)
    if user is not None and user.get("is_enabled") and user.get("phone_number") is not None:
        await message.reply_text(text="Привет!\n\nЯ в полном порядке, работаем 🫡", parse_mode=enums.ParseMode.HTML)
    if user is not None and not user.get("is_enabled"):
        await message.reply_text(text="Чтобы пользоваться ботом тебе необходимо подключить его. \n\nДля получения инструкций по подключению нажми на кнопку ниже:")
    if user is None:
        keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton("Отправить контакт ☎️", request_contact=True)]],
                                       one_time_keyboard=True, resize_keyboard=True)
        await message.reply_text(
            text="🕵️‍♂ Привет! Чтобы узнать о возможностях бота — зергистрируйся.\n\nПришли мне свой номер телефона нажав на кнопку ниже:",
            reply_markup=keyboard, parse_mode=enums.ParseMode.HTML)