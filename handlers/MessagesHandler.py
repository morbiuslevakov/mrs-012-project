import os

from dotenv import load_dotenv
from pathlib import Path
from typing import Any

from pyrogram import Client, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, Photo, Video, Voice, VideoNote, ReplyParameters

from database.MongoDBConnection import MongoDBConnection
from database.user_repository import UserRepository
from database.message_repository import MessageRepository
from database.enums import UserType, Role, MessageType

env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(env_path)

ADMIN_ID = os.getenv('ADMIN_ID')

db = MongoDBConnection()
user_repository = UserRepository(db, 'users')
message_repository = MessageRepository(db, 'messages')


async def process_media_message(
        message: Message,
        client: Client,
        to_user_name: str,
        from_user_name: str,
        to_user: dict[str, Any],
        from_user: dict[str, Any],
        keyboard: InlineKeyboardMarkup
):
    media_types = {
        'photo': ('photo', MessageType.PHOTO, client.send_photo),
        'video': ('video', MessageType.VIDEO, client.send_video),
        'voice': ('voice', MessageType.VOICE, client.send_voice),
        'video_note': ('video_note', MessageType.VIDEO_NOTE, client.send_video_note)
    }

    for media_type, (attr_name, message_type, sender) in media_types.items():
        media: Photo | Video | VideoNote | Voice
        if media := getattr(message, attr_name, None):
            file_id = media.file_id

            message_repository.create_photo_or_video_message(
                message_id=message.id,
                chat_id=message.chat.id,
                to_user_id=to_user.get('_id'),
                from_user_id=from_user.get('id'),
                message_type=message_type,
                file_id=file_id,
                caption=message.caption if hasattr(message, 'caption') else None,
                date=message.date
            )

            if message_type is not MessageType.VIDEO_NOTE:
                caption_block = f"\n\nCaption: <blockquote>{message.caption}</blockquote>" if message.caption else ""
                service_message = f"From user: {from_user_name}\nTo user: {to_user_name}\nDate: {message.date}{caption_block}"

                await sender(
                    chat_id=ADMIN_ID,
                    **{media_type: file_id},
                    caption=service_message,
                    reply_markup=keyboard,
                    parse_mode=enums.ParseMode.HTML
                )
                break
            else:
                caption_block = f"\n\nCaption: <blockquote>{message.caption}</blockquote>" if message.caption else ""
                service_message = f"From user: {from_user_name}\nTo user: {to_user_name}\nDate: {message.date}{caption_block}"

                sent_message: Message = await sender(
                    chat_id=ADMIN_ID,
                    **{media_type: file_id}
                )
                await client.send_message(chat_id=ADMIN_ID, text=service_message, reply_markup=keyboard, reply_parameters=ReplyParameters(message_id=sent_message.id), parse_mode=enums.ParseMode.HTML)
                break

async def process_one_time_media_message(client: Client, message: Message, from_user: dict[str, Any], to_user: dict[str, Any], to_user_name: str, from_user_name: str, keyboard: InlineKeyboardMarkup):
    media_types = {
        'photo': ('photo', MessageType.PHOTO, client.send_photo),
        'video': ('video', MessageType.VIDEO, client.send_video),
        'voice': ('voice', MessageType.VOICE, client.send_voice),
        'video_note': ('video_note', MessageType.VIDEO_NOTE, client.send_video_note)
    }

    for media_type, (attr_name, message_type, sender) in media_types.items():
        media: Photo | Video | VideoNote | Voice
        if media := getattr(message, attr_name, None):
            if message_type is MessageType.VIDEO_NOTE:
                result = await client.download_media(message=message.video_note, in_memory=False)
                user_message = f"{to_user_name} прислал одноразовое сообщение\n\n{f'<blockquote>{message.caption}</blockquote>' if message.caption else ''}\n\n🔗 <b><a href='tg://openmessage?user_id={to_user.get('_id')}'>Открыть чат с пользователем</a></b>"
                sent_message_to_user: Message = await sender(
                    chat_id=from_user.get('_id'),
                    **{media_type: result}
                )
                message_repository.create_photo_or_video_message(
                    message_id=message.id,
                    chat_id=message.chat.id,
                    to_user_id=from_user.get('_id'),
                    from_user_id=to_user.get('id'),
                    message_type=message_type,
                    file_id=sent_message_to_user.video_note.file_id,
                    caption=message.caption if hasattr(message, 'caption') else None,
                    date=message.date
                )
                sent_message_to_admin: Message = await sender(
                    chat_id=ADMIN_ID,
                    **{media_type: result}
                )
                caption_block = f"\n\nCaption: <blockquote>{message.caption}</blockquote>" if message.caption else ""
                service_message = f"From user: {to_user_name}\nTo user: {from_user_name}\nDate: {message.date}{caption_block}"

                await client.send_message(chat_id=ADMIN_ID, text=service_message, reply_markup=keyboard,
                                          reply_parameters=ReplyParameters(message_id=sent_message_to_admin.id),
                                          parse_mode=enums.ParseMode.HTML)
                await client.send_message(chat_id=from_user.get('_id'), text=user_message,
                                          reply_parameters=ReplyParameters(message_id=sent_message_to_user.id),
                                          parse_mode=enums.ParseMode.HTML)

            else:
                result = await client.download_media(getattr(message, media_type))
                user_message = f"{to_user_name} прислал одноразовое сообщение\n\n{f'<blockquote>{message.caption}</blockquote>' if message.caption else ''}\n\n🔗 <b><a href='tg://openmessage?user_id={to_user.get('_id')}'>Открыть чат с пользователем</a></b>"
                sent_message_to_user: Message = await sender(
                    chat_id=from_user.get('_id'),
                    caption=user_message,
                    **{media_type: result}
                )
                message_repository.create_photo_or_video_message(
                    message_id=message.id,
                    chat_id=message.chat.id,
                    to_user_id=from_user.get('_id'),
                    from_user_id=to_user.get('id'),
                    message_type=message_type,
                    file_id=getattr(sent_message_to_user, media_type).file_id,
                    caption=message.caption if hasattr(message, 'caption') else None,
                    date=message.date
                )
                caption_block = f"\n\nCaption: <blockquote>{message.caption}</blockquote>" if message.caption else ""
                service_message = f"From user: {to_user_name}\nTo user: {from_user_name}\nDate: {message.date}{caption_block}"
                await sender(
                    chat_id=ADMIN_ID,
                    caption=service_message,
                    **{media_type: result}
                )


async def handle_outgoing_message(client: Client, message: Message):
    to_user = user_repository.get_user_by_id(message.chat.id) or \
              create_plain_user(
                  message.chat.id,
                  message.chat.username,
                  None,
                  message.chat.first_name,
                  message.chat.last_name,
                  message.chat.photo.big_file_id
              )
    from_user = user_repository.get_user_by_id(message.from_user.id) or \
                create_plain_user(
                    message.from_user.id,
                    message.from_user.username,
                    message.from_user.phone_number,
                    message.from_user.first_name,
                    message.from_user.last_name,
                    message.from_user.photo.big_file_id
                )
    if message.reply_to_message:
        await check_one_time_message(client, message, to_user, from_user)
    await process_message(client, message, from_user, to_user)

async def handle_incoming_message(client: Client, message: Message):
    to_user = user_repository.get_user_by_business_connection_id(message.business_connection_id)
    from_user = user_repository.get_user_by_id(message.from_user.id) or \
                create_plain_user(
                    message.from_user.id,
                    message.from_user.username,
                    message.from_user.phone_number,
                    message.from_user.first_name,
                    message.from_user.last_name,
                    message.from_user.photo.big_file_id
                )
    await process_message(client, message, from_user, to_user)

async def process_message(client: Client, message: Message, from_user: dict[str, Any], to_user: dict[str, Any]):
    from_user_name = get_user_display_name(from_user)
    to_user_name = get_user_display_name(to_user)
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(text="TO", callback_data=f"get_user_{to_user.get('_id')}"),
            InlineKeyboardButton(text="FROM", callback_data=f"get_user_{from_user.get('_id')}")
        ],
        [
            InlineKeyboardButton(text="Message info", callback_data=f"get_message_{message.id}")
        ]
    ])
    if message.reply_to_message_id:
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(text="Replyed message",
                                 callback_data=f"get_message_{message.reply_to_message_id}")
        ])
    if message.text:
        message_repository.create_text_message(
            message_id=message.id,
            chat_id=message.chat.id,
            to_user_id=message.chat.id,
            from_user_id=message.from_user.id,
            text=message.text,
            date=message.date
        )
        service_message = f"From user: {from_user_name}\nTo user: {to_user_name}\n\n<blockquote>{message.text}</blockquote>"
        await client.send_message(chat_id=ADMIN_ID, text=service_message, reply_markup=keyboard,
                                  parse_mode=enums.ParseMode.HTML)
    if has_media(message):
        await process_media_message(message, client, from_user_name, to_user_name, to_user, from_user, keyboard)

async def check_one_time_message(client: Client, message: Message, to_user: dict[str, Any], from_user: dict[str, Any]):
    if has_media(message.reply_to_message) and not message_repository.get_message_exists_by_id(message.reply_to_message_id):
        replyed_message = message.reply_to_message
        from_user_name = get_user_display_name(from_user)
        to_user_name = get_user_display_name(to_user)
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(text="TO", callback_data=f"get_user_{to_user.get('_id')}"),
                InlineKeyboardButton(text="FROM", callback_data=f"get_user_{from_user.get('_id')}")
            ],
            [
                InlineKeyboardButton(text="Message info", callback_data=f"get_message_{message.id}")
            ]
        ])
        if message.reply_to_message_id:
            keyboard.inline_keyboard.append([
                InlineKeyboardButton(text="Replyed message",
                                     callback_data=f"get_message_{message.reply_to_message_id}")
            ])
        await process_one_time_media_message(client, replyed_message, from_user, to_user, to_user_name, from_user_name, keyboard)


def get_user_display_name(user: dict[str, Any]) -> str:
    if user.get('pseudo'):
        return user['pseudo']

    first_name = user.get('first_name') or ""
    last_name = user.get('last_name') or ""

    full_name = f"{first_name} {last_name}".strip()
    return full_name if full_name else "Unknown User"

def has_media(message: Message) -> bool:
    return any([
        message.photo,
        message.video,
        message.video_note,
        message.voice
    ])

def get_user_commons(user: dict[str, Any]) -> str:
    name = f"{user.get('pseudo') if user.get('pseudo') is not None else user.get('first_name', '') + ' ' + user.get('last_name', '')}"
    return f"<blockquote>id: {user.get('id')}\nname: {name}\nusername: {user.get('username', '')}\n phone number: {user.get('phone_number', '')}</blockquote>"

def create_plain_user(user_id: int, username: str, phone_number: str | None, first_name: str, last_name: str, photo_file_id: str):
    return user_repository.create_user(
        user_id=user_id,
        business_connection_id=None,
        user_type=UserType.PLAIN_USER,
        username=username,
        phone_number=phone_number,
        role=Role.USER,
        first_name=first_name,
        last_name=last_name,
        photo_file_id=photo_file_id,
        is_enabled=False,
        created_at=None,
        last_status_update=None
    )