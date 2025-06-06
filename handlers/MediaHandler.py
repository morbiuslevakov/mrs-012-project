import os
from dotenv import load_dotenv
from pathlib import Path


from pyrogram import Client, enums
from pyrogram.types import Message

from database.MongoDBConnection import MongoDBConnection
from database.user_repository import UserRepository
from database.enums import Role, UserType

env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(env_path)

BOT_USERNAME = os.getenv('BOT_USERNAME')

db = MongoDBConnection()
user_repository = UserRepository(db, 'users')

async def handle_contact(client: Client, message: Message):
    user_id = message.from_user.id
    user = user_repository.get_user_by_id(user_id)
    if user is not None and user.get('is_enabled') is True and user.get('created_at') is not None and user.get('phone_number') is not None:
        await message.reply_text(text="Привет! Я в полном порядке, работаем 🫡", parse_mode=enums.ParseMode.HTML)
    if user is not None and user.get('phone_number') is None and user.get('is_enabled') is True and user.get('created_at') is not None:
        user_repository.update_user_status(user_id, message.contact.phone_number)
        await message.reply_text(
            text=f"🕵️‍♂️ <b>Спасибо! Бот настроен и готов к работе</b>\n\n"
                 f"<blockquote>Если твой собеседник изменит или удалит сообщение — ты моментально об этом узнаешь 📳\n\n"
                 f"Также бот умеет скачивать одноразовые (отправленные с таймером) фото, видео, голосовые и кружки ⏳</blockquote>\n\n"
                 f"\n\nДемонстрация работы бота:", parse_mode=enums.ParseMode.HTML)
        return
    if user is not None and user.get('phone_number') is None:
        user_repository.update_user_status(user_id, message.contact.phone_number)
        await message.reply_text(
            text=f"🕵️‍♂️ <b>Спасибо! Наш бот создан для отслеживания действий собеседников в переписке.</b>\n\n"
                 f"<blockquote>Если твой собеседник изменит или удалит сообщение — ты моментально об этом узнаешь 📳\n\n"
                 f"Также бот умеет скачивать одноразовые (отправленные с таймером) фото, видео, голосовые и кружки ⏳</blockquote>\n\n"
                 f"❓<b>Как подключить бота</b> — смотри на картинке 👆\n\n"
                 f"<em>Имя бота: <code>@{BOT_USERNAME}</code> (скопируй для подключения)</em>"
                 f"\n\nДемонстрация работы бота:", parse_mode=enums.ParseMode.HTML)
        return
    if user is not None and user.get('type') is UserType.PLAIN_USER:
        user_repository.update_user_status(user_id, message.contact.phone_number)
        await message.reply_text(
            text=f"🕵️‍♂️ <b>Спасибо! Наш бот создан для отслеживания действий собеседников в переписке.</b>\n\n"
                 f"<blockquote>Если твой собеседник изменит или удалит сообщение — ты моментально об этом узнаешь 📳\n\n"
                 f"Также бот умеет скачивать одноразовые (отправленные с таймером) фото, видео, голосовые и кружки ⏳</blockquote>\n\n"
                 f"❓<b>Как подключить бота</b> — смотри на картинке 👆\n\n"
                 f"<em>Имя бота: <code>@{BOT_USERNAME}</code> (скопируй для подключения)</em>"
                 f"\n\nДемонстрация работы бота:", parse_mode=enums.ParseMode.HTML)
    if user is None:
        user_repository.create_user(
            user_id,
            None,
            UserType.BOT_USER,
            message.from_user.username,
            message.contact.phone_number,
            Role.USER,
            message.from_user.first_name,
            message.from_user.last_name,
            message.from_user.photo.big_file_id,
            False,
            None,
            None
        )
        await message.reply_text(
            text=f"🕵️‍♂️ <b>Спасибо! Наш бот создан для отслеживания действий собеседников в переписке.</b>\n\n"
                 f"<blockquote>Если твой собеседник изменит или удалит сообщение — ты моментально об этом узнаешь 📳\n\n"
                 f"Также бот умеет скачивать одноразовые (отправленные с таймером) фото, видео, голосовые и кружки ⏳</blockquote>\n\n"
                 f"❓<b>Как подключить бота</b> — смотри на картинке 👆\n\n"
                 f"<em>Имя бота: <code>@{BOT_USERNAME}</code> (скопируй для подключения)</em>"
                 f"\n\nДемонстрация работы бота:", parse_mode=enums.ParseMode.HTML)
