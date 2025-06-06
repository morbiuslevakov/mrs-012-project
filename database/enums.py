import enum

class Role(enum.Enum):
    ADMIN = 1
    SUPERUSER = 2
    USER = 3

class UserType(enum.Enum):
    BOT_USER = 1
    PLAIN_USER = 2

class MessageType(enum.Enum):
    TEXT = 1
    PHOTO = 2
    VIDEO = 3
    VIDEO_NOTE = 4
    VOICE = 5
    STICKER = 6
    GIF = 7

class MessageDirection(enum.Enum):
    OUTGOING = 1
    INCOMING = 2