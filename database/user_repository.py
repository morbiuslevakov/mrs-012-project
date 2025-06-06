from datetime import datetime

from pymongo.errors import DuplicateKeyError
from typing import Optional, Dict, Any

from database.MongoDBConnection import MongoDBConnection
from database.enums import Role, UserType

class UserRepository:
    def __init__(self, db_connection: MongoDBConnection, collection_name: str = 'users'):
        self.collection = db_connection.db[collection_name]

    def create_user(self, user_id: int, business_connection_id: str | None, user_type: UserType, username: str, phone_number: str | None, role: Role, first_name: str, last_name: str, photo_file_id: str, is_enabled: bool, created_at: datetime | None, last_status_update: datetime | None) -> Optional[Dict[str, Any]]:
        user_data = {
            '_id': user_id,
            'business_connection_id': business_connection_id,
            'type': user_type.name,
            'username': username,
            'phone_number': phone_number,
            'role': role.name,
            'first_name': first_name,
            'last_name': last_name,
            'photo_file_id': photo_file_id,
            'pseudo': None,
            'is_enabled': is_enabled,
            'created_at': created_at,
            'last_status_update': last_status_update
        }

        try:
            result = self.collection.insert_one(user_data)
            if result.inserted_id:
                return self.get_user_by_id(user_id)
            return None
        except DuplicateKeyError:
            return None

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        return self.collection.find_one({'_id': user_id})

    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        user = self.collection.find_one({'username': username})
        return user

    def get_user_by_business_connection_id(self, business_connection_id: str):
        user = self.collection.find_one({'business_connection_id': business_connection_id})
        return user

    def update_user(self, user_id: int, new_username: str) -> bool:
        result = self.collection.update_one(
            {'_id': user_id},
            {'$set': {'username': new_username}}
        )
        return result.modified_count > 0

    def delete_user(self, user_id: int) -> bool:
        result = self.collection.delete_one({'_id': user_id})
        return result.deleted_count > 0

    def update_user_connection_and_status(self, user_id: int, business_connection_id: str, update_time: datetime, is_enabled: bool, created_at: datetime, phone_number: str):
        self.collection.update_one(
            {'_id': user_id},
            {'$set': {'business_connection_id': business_connection_id, 'last_status_update': update_time,
                      'is_enabled': is_enabled, 'created_at': created_at, 'type': UserType.BOT_USER.name, 'phone_number': phone_number}}
        )

    def update_user_connection(self, user_id: int, business_connection_id: str, update_time: datetime, is_enabled: bool, created_at: datetime):
        self.collection.update_one(
            {'_id': user_id},
            {'$set': {'business_connection_id': business_connection_id ,'last_status_update': update_time, 'is_enabled': is_enabled, 'created_at': created_at}}
        )

    def update_user_status(self, user_id: int, phone_number: str):
        self.collection.update_one(
            {'_id': user_id},
            {'$set': {'type': UserType.BOT_USER.name, 'phone_number': phone_number}}
        )

    def add_phone_number(self, user_id: int, phone_number: str):
        result = self.collection.update_one(
            {'_id': user_id},
            {'$set': {'phone_number': phone_number}}
        )
        return result.modified_count > 0

    def add_pseudo(self, user_id: int, pseudo: str):
        result = self.collection.update_one(
            {'_id': user_id},
            {'$set': {'pseudo': pseudo}}
        )
        return result.modified_count > 0