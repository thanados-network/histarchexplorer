from typing import Any, Optional

from flask_login import UserMixin

from histarchexplorer.database.user import get_by_username, get_user_by_id


class User(UserMixin):
    def __init__(self, row: Any) -> None:
        self.id = row.id
        self.active = row.active == 1
        self.username = row.username
        self.password = row.password
        self.group = row.group_name
        self.real_name = row.real_name

    @staticmethod
    def get_by_id(user_id: int) -> Optional['User']:
        if user_data := get_user_by_id(user_id):
            return User(user_data)
        return None  # e.g. obsolete session values

    @staticmethod
    def get_by_username(username: str) -> Optional['User']:
        user_data = get_by_username(username)
        return User(user_data) if user_data else None
