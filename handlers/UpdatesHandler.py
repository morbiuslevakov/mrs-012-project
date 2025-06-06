import os
from dotenv import load_dotenv
from pathlib import Path

from pyrogram import Client, enums
from pyrogram.types import BusinessConnection, ReplyKeyboardMarkup, KeyboardButton

from database.MongoDBConnection import MongoDBConnection
from database.user_repository import UserRepository
from database.enums import Role, UserType

env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(env_path)

ADMIN_ID = os.getenv('ADMIN_ID')
BOT_USERNAME = os.getenv('BOT_USERNAME')

# MongoDB initialization
db = MongoDBConnection()
user_repository = UserRepository(db, 'users')


async def handle_connection_update(client: Client, connection: BusinessConnection):
    user_id = connection.user.id
    user = user_repository.get_user_by_id(user_id)
    keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton("Отправить контакт ☎️", request_contact=True)]],
                                   one_time_keyboard=True, resize_keyboard=True)
    if user is not None and not connection.is_enabled and user.get("created_at") is not None:
        user_repository.update_user_connection(user_id, connection.id, connection.date, connection.is_enabled, connection.date)
        username = user.get('username') if user.get('username') else None
        phone_number = user.get('phone_number') if user.get('phone_number') else None
        message = (
            "🟢 <b>Client connection interrupted</b>\n\n"
            f"🆔 <b>ID:</b> <code>{user.get('_id')}</code>\n"
            f"👤 <b>Username:</b> {f'@{username}' if user.get('username') else '—'}\n"
            f"📛 <b>Name:</b> {user.get('first_name', '')} {user.get('last_name', '')}\n"
            f"📱 <b>Phone:</b> <code>{phone_number}</code>"
        )
        await client.send_message(chat_id=ADMIN_ID, text=message, parse_mode=enums.ParseMode.HTML)
    if user is not None and connection.is_enabled and user.get("created_at") is not None:
        user_repository.update_user_connection(user_id, connection.id, connection.date, connection.is_enabled, connection.date)
        username = user.get('username') if user.get('username') else None
        phone_number = user.get('phone_number') if user.get('phone_number') else None
        message = (
            "🟢 <b>Client connection restored</b>\n\n"
            f"🆔 <b>ID:</b> <code>{user.get('_id')}</code>\n"
            f"👤 <b>Username:</b> {f'@{username}' if user.get('username') else '—'}\n"
            f"📛 <b>Name:</b> {user.get('first_name', '')} {user.get('last_name', '')}\n"
            f"📱 <b>Phone:</b> <code>{phone_number}</code>"
        )
        await client.send_message(chat_id=ADMIN_ID, text=message, parse_mode=enums.ParseMode.HTML)
    if user is None and connection.is_enabled:
        user = user_repository.create_user(
            user_id,
            connection.id,
            UserType.BOT_USER,
            connection.user.username,
            connection.user.phone_number,
            Role.USER,
            connection.user.first_name,
            connection.user.last_name,
            connection.user.photo.big_file_id,
            connection.is_enabled,
            connection.date,
            connection.date
        )
        username = user.get('username') if user.get('username') else None
        phone_number = user.get('phone_number') if user.get('phone_number') else None
        message = (
            "🟢 <b>New client connection</b>\n\n"
            f"🆔 <b>ID:</b> <code>{user.get('_id')}</code>\n"
            f"👤 <b>Username:</b> {f'@{username}' if user.get('username') else None}\n"
            f"📛 <b>Name:</b> {user.get('first_name', '')} {user.get('last_name', '')}\n"
            f"📱 <b>Phone:</b> <code>{phone_number}</code>"
        )
        await client.send_message(
            chat_id=user_id,
            text="🕵️‍♂ Привет! Чтобы узнать о возможностях бота — зергистрируйся.\n\nПришли мне свой номер телефона нажав на кнопку ниже:",
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.HTML
        )
        await client.send_message(
            chat_id=ADMIN_ID,
            text=message,
            parse_mode=enums.ParseMode.HTML
        )
    if user is not None and connection.is_enabled and user.get('created_at') is None and user.get('type') == UserType.PLAIN_USER.name:
        user_repository.update_user_connection(user_id, connection.id, connection.date, connection.is_enabled, connection.date)
        username = user.get('username') if user.get('username') else None
        phone_number = user.get('phone_number') if user.get('phone_number') else None
        message = (
            "🟢 <b>New client connection</b>\n\n"
            f"🆔 <b>ID:</b> <code>{user.get('_id')}</code>\n"
            f"👤 <b>Username:</b> {f'@{username}' if user.get('username') else None}\n"
            f"📛 <b>Name:</b> {user.get('first_name', '')} {user.get('last_name', '')}\n"
            f"📱 <b>Phone:</b> <code>{phone_number}</code>"
        )
        await client.send_message(
            chat_id=ADMIN_ID,
            text=message,
            parse_mode=enums.ParseMode.HTML
        )
        await client.send_message(
            chat_id=user_id,
            text="🕵️‍♂ Привет! Чтобы узнать о возможностях бота — зергистрируйся.\n\nПришли мне свой номер телефона нажав на кнопку ниже:",
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.HTML
        )
    if user is not None and connection.is_enabled and user.get('created_at') is None and user.get('type') == UserType.BOT_USER.name and user.get('phone_number'):
        user_repository.update_user_connection(user_id, connection.id, connection.date, connection.is_enabled, connection.date)
        username = user.get('username') if user.get('username') else None
        phone_number = user.get('phone_number') if user.get('phone_number') else None
        message = (
            "🟢 <b>New client connection</b>\n\n"
            f"🆔 <b>ID:</b> <code>{user.get('_id')}</code>\n"
            f"👤 <b>Username:</b> {f'@{username}' if user.get('username') else None}\n"
            f"📛 <b>Name:</b> {user.get('first_name', '')} {user.get('last_name', '')}\n"
            f"📱 <b>Phone:</b> <code>{phone_number}</code>"
        )
        await client.send_message(
            chat_id=ADMIN_ID,
            text=message,
            parse_mode=enums.ParseMode.HTML
        )
        await client.send_message(
            chat_id=user_id,
            text=f"🕵️‍♂️ <b>Спасибо! Наш бот создан для отслеживания действий собеседников в переписке.</b>\n\n"
                 f"<blockquote>Если твой собеседник изменит или удалит сообщение — ты моментально об этом узнаешь 📳\n\n"
                 f"Также бот умеет скачивать одноразовые (отправленные с таймером) фото, видео, голосовые и кружки ⏳</blockquote>\n\n"
                 f"❓<b>Как подключить бота</b> — смотри на картинке 👆\n\n"
                 f"<em>Имя бота: <code>@{BOT_USERNAME}</code> (скопируй для подключения)</em>"
                 f"\n\nДемонстрация работы бота:", parse_mode=enums.ParseMode.HTML)
