import os
from dotenv import load_dotenv
from pathlib import Path
from typing import Any

from pyrogram import Client
from pyrogram import enums
from pyrogram.types import ReplyParameters
from pyrogram.raw.types import UpdateBotDeleteBusinessMessage
from database.enums import MessageType

from database.MongoDBConnection import MongoDBConnection
from database.user_repository import UserRepository
from database.message_repository import MessageRepository

env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(env_path)

ADMIN_ID = os.getenv('ADMIN_ID')

db = MongoDBConnection()
user_repository = UserRepository(db, 'users')
message_repository = MessageRepository(db, 'messages')

async def handle_raw_update(client, update, users, chats):
    if isinstance(update, UpdateBotDeleteBusinessMessage):
        await handle_deleted_messages(client, update, users, chats)

async def handle_deleted_messages(client: Client, update: UpdateBotDeleteBusinessMessage, users: Any, chats: Any):
    to_user = user_repository.get_user_by_business_connection_id(update.connection_id)
    from_user = user_repository.get_user_by_id(update.peer.user_id)
    from_user_name = get_user_display_name(from_user)
    for message_id in update.messages:
        deleted_message = message_repository.get_message_by_id(message_id)
        if deleted_message.get('type') == 'TEXT':
            text = f"{from_user_name} удалил(а) сообщение\n\n<blockquote>{deleted_message.get('text')}</blockquote>\n\n🔗 <b><a href='tg://openmessage?user_id={from_user.get('_id')}'>Открыть чат с пользователем</a></b>"
            await client.send_message(chat_id=to_user.get('_id'), text=text, parse_mode=enums.ParseMode.HTML)
        else:
            caption = f"{from_user_name} удалил(а) сообщение\n\nОписание: \n<blockquote>{deleted_message.get('caption')}</blockquote>\n\n🔗 <b><a href='tg://openmessage?user_id={from_user.get('_id')}'>Открыть чат с пользователем</a></b>"
            await process_media(client, to_user, caption, deleted_message)

async def process_media(client: Client, user: dict[str, Any], caption: str, deleted_message: dict[str, Any]):
    media_types = {
        'PHOTO': (MessageType.PHOTO, client.send_photo),
        'VOICE': (MessageType.VOICE, client.send_voice),
        'VIDEO_NOTE': (MessageType.VIDEO_NOTE, client.send_video_note)
    }

    message_type = deleted_message.get('type')

    if message_type in media_types:
        handler_type, sender = media_types[message_type]
        file_id = deleted_message.get('file_id')

        if message_type != 'VIDEO_NOTE':
            await sender(
                chat_id=user.get('_id'),
                **{str(message_type).lower(): file_id},
                caption=caption,
                parse_mode=enums.ParseMode.HTML
            )
        else:
            sent_message = await sender(
                chat_id=user.get('_id'),
                video_note=file_id
            )
            await client.send_message(
                chat_id=user.get('_id'),
                text=caption,
                reply_parameters=ReplyParameters(message_id=sent_message.id),
                parse_mode=enums.ParseMode.HTML
            )

def get_user_display_name(user: dict[str, Any]) -> str:
    if user.get('pseudo'):
        return user['pseudo']

    first_name = user.get('first_name') or ""
    last_name = user.get('last_name') or ""

    full_name = f"{first_name} {last_name}".strip()
    return full_name if full_name else "Unknown User"