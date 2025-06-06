import os
from dotenv import load_dotenv
from pathlib import Path
from typing import Any

from pyrogram import Client, enums
from pyrogram.types import CallbackQuery, MessageEntity
from pyrogram.enums import MessageEntityType

from database.MongoDBConnection import MongoDBConnection
from database.user_repository import UserRepository

env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(env_path)

ADMIN_ID = os.getenv('ADMIN_ID')

db = MongoDBConnection()
user_repository = UserRepository(db, 'users')

async def handle_get_user_callback(client: Client, callback_query: CallbackQuery):
    user_id = int(callback_query.data.split("_")[-1])
    user = user_repository.get_user_by_id(user_id)
    user_commons = get_user_commons(user)
    if user.get('photo_file_id'):
        await client.send_photo(chat_id=ADMIN_ID, photo=user.get('photo_file_id'), caption=user_commons, parse_mode=enums.ParseMode.HTML)
    else:
        await client.send_message(chat_id=ADMIN_ID, text=user_commons, parse_mode=enums.ParseMode.HTML)

def get_user_commons(user: dict[str, Any]) -> str:
    name = get_user_display_name(user)
    return f"ℹ️ ID: <code>{user.get('_id')}</code>\n🔑 Type: <code>{user.get('type')}</code>\n🧑‍💻 Name: {name}\n📭 Username: {'@' + user.get('username') if user.get('username') else ''}\n📱 Phone number: <code>{user.get('phone_number') if user.get('phone_number') else ''}</code>\n\n🔗 <b><a href='tg://openmessage?user_id={user.get('_id')}'>Вечная ссылка</a></b>"

def get_user_display_name(user: dict[str, Any]) -> str:
    if user.get('pseudo'):
        return user['pseudo']

    first_name = user.get('first_name') or ""
    last_name = user.get('last_name') or ""

    full_name = f"{first_name} {last_name}".strip()
    return full_name if full_name else "Unknown User"
