from abc import ABC, abstractmethod
from pyrogram.types import Message

from pymongo.collection import Collection

class MessageProcessor(ABC):
    @abstractmethod
    def to_dict(self) -> dict:
        pass

    @abstractmethod
    def filter_fields(self, data: dict) -> dict:
        pass

class TextMessageProcessor(MessageProcessor):
    def __init__(self, message: Message):
        self.message = message

    def to_dict(self) -> dict:
        data = {
            "message_id": self.message.id,
            "chat_id": self.message.chat.id,
            "date": self.message.date,
            "text": self.message.text,
            "from_user": self.message.from_user.id if self.message.from_user else None
        }
        return self.filter_fields(data)

    def filter_fields(self, data: dict) -> dict:
        allowed_fields = ["message_id", "chat_id", "date", "text", "from_user"]
        return {k: v for k, v in data.items() if k in allowed_fields}

class MediaMessageProcessor(MessageProcessor):
    def __init__(self, message: Message):
        self.message = message

    def to_dict(self) -> dict:
        data = {
            "message_id": self.message.id,
            "chat_id": self.message.chat.id,
            "date": self.message.date,
            "media_type": self.message.media.value if self.message.media else None,
            "file_id": getattr(self.message, self.message.media.value).file_id if self.message.media else None
        }
        return self.filter_fields(data)

    def filter_fields(self, data: dict) -> dict:
        allowed_fields = ["message_id", "chat_id", "date", "media_type", "file_id"]
        return {k: v for k, v in data.items() if k in allowed_fields}

def get_message_processor(message: Message) -> MessageProcessor:
    if message.text:
        return TextMessageProcessor(message)
    elif message.media:
        return MediaMessageProcessor(message)
    else:
        raise ValueError("Unsupported message type")

async def handle_message(message: Message, collection: Collection):
    try:
        processor = get_message_processor(message)
        message_dict = processor.to_dict()
        collection.insert_one(message_dict)
    except Exception as e:
        print(f"Error processing message: {e}")