from datetime import datetime

from pymongo.errors import DuplicateKeyError
from typing import Optional, Dict, Any

from database.MongoDBConnection import MongoDBConnection
from database.enums import MessageType

class MessageRepository:
    def __init__(self, db_connection: MongoDBConnection, collection_name: str = 'messages'):
        self.collection = db_connection.db[collection_name]

    def get_message_by_id(self, message_id: int) -> Optional[Dict[str, Any]]:
        return self.collection.find_one({'_id': message_id})

    def get_message_exists_by_id(self, message_id: int):
        return self.collection.count_documents({'_id': message_id}) >= 1

    def insert_message(self, message_id: int, message: Optional[Dict[str, Any]]):
        try:
            result = self.collection.insert_one(message)
            if result.inserted_id:
                return self.get_message_by_id(message_id)
            return None
        except DuplicateKeyError:
            return None

    def create_text_message(self, message_id: int, chat_id: int, to_user_id: int, from_user_id: int, text: str,
                            date: datetime) -> Optional[Dict[str, Any]]:
        message_data = {
            '_id': message_id,
            'chat_id': chat_id,
            'to_user_id': to_user_id,
            'from_user_id': from_user_id,
            'type': MessageType.TEXT.name,
            'text': text,
            'date': date
        }
        return self.insert_message(message_id, message_data)

    """
        creating photo, video, voice, video note messages
    """
    def create_photo_or_video_message(self, message_id: int, chat_id: int, to_user_id: int, from_user_id: int, message_type: MessageType, file_id: str, caption: str | None, date: datetime):
        message_data = {
            '_id': message_id,
            'chat_id': chat_id,
            'to_user_id': to_user_id,
            'from_user_id': from_user_id,
            'type': message_type.name,
            'file_id': file_id,
            'caption': caption,
            'date': date
        }
        return self.insert_message(message_id, message_data)

    def create_gif_message(self, message_id: int, chat_id: int, to_user_id: int, from_user_id: int, date: datetime):
        pass

    def create_sticker_message(self, message_id: int, chat_id: int, to_user_id: int, from_user_id: int, date: datetime):
        pass