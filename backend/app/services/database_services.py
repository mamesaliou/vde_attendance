from typing import Optional
from datetime import datetime

from app.database.models.user import UserDB
from app.database.entrypoint_db import EntryPointDb
from app.models.invitation_code import InvitationCode
from app.models.revoked_token import RevokedToken
from app.models.user import User
from app.tools.page_limit_query import page_limit_query
from app.tools.singleton import Singleton


class DbService(metaclass=Singleton):

    def __init__(self):
        self.__entrypoint_db = None


    @property
    def entrypoint_db(self):
        if self.__entrypoint_db is None:
            self.__entrypoint_db = EntryPointDb()
        return self.__entrypoint_db

    async def create_invitation_code(self, code: str, expires_at: datetime, created_by: str, is_superuser: bool = False):
        with self.entrypoint_db.invitation_code as invitation_service:
            db_invitation_code = invitation_service.create(code, expires_at, created_by, is_superuser)
            return InvitationCode.from_db(db_invitation_code)

    async def get_invitation_code(self, code: str):
        with self.entrypoint_db.invitation_code as invitation_service:
            db_invitation_code = invitation_service.get_by_code(code)
            return InvitationCode.from_db(db_invitation_code)

    async def update_invitation_code(self, code: str, used_at: datetime):
        with self.entrypoint_db.invitation_code as invitation_service:
            db_invitation_code = invitation_service.update(code, used_at=used_at)
            return InvitationCode.from_db(db_invitation_code)

    async def create_revoked_token(self, jti: str, expires_at: datetime, revoked_by: str, device_info: str = None):
        with self.entrypoint_db.revoked_token as revoked_service:
            db_revoked_token = revoked_service.create(jti, expires_at, revoked_by, device_info)
            return RevokedToken.from_db(db_revoked_token)

    async def get_revoked_token(self, jti: str):
        with self.entrypoint_db.revoked_token as revoked_service:
            db_revoked_token = revoked_service.get_by_jti(jti)
            return RevokedToken.from_db(db_revoked_token)

    async def delete_revoked_token(self, jti: str):
        with self.entrypoint_db.revoked_token as revoked_service:
            revoked_service.delete(jti=jti)

    async def cleanup_expired_tokens(self):
        with self.entrypoint_db.revoked_token as revoked_service:
            revoked_service.cleanup_expired()

    async def create_user(self, username: str, email: str, handle: str, hashed_password: str, is_superuser: bool = False,
                          is_active: bool = False, first_name: Optional[str] = None, last_name: Optional[str] = None,
                          code: Optional[str] = None):
        with self.entrypoint_db.user as user_service:
            db_user = user_service.create(
                username=username,
                email=email,
                handle=handle,
                hashed_password=hashed_password,
                is_superuser=is_superuser,
                is_active=is_active,
                first_name=first_name,
                last_name=last_name,
                code=code
            )
            return User.from_db(db_user)

    async def get_user(self, user_id: int) -> User:
        with self.entrypoint_db.user as user_db:
            db_user = user_db.get(user_id)
            return User.from_db(db_user)

    async def get_unique_user(self, **kwargs) -> User:
        with self.entrypoint_db.user as user_db:
            db_user = user_db.get_user(**kwargs)
            return User.from_db(db_user)

    async def get_user_by_username(self, username: str) -> User:
        with self.entrypoint_db.user as user_db:
            db_user = user_db.get_by_username(username)
            return User.from_db(db_user)

    async def get_user_by_handle(self, handle: str) -> User:
        with self.entrypoint_db.user as user_db:
            db_user = user_db.get_by_handle(handle)
            return User.from_db(db_user)

    async def get_user_by_email(self, email: str) -> User:
        with self.entrypoint_db.user as user_db:
            db_user = user_db.get_by_email(email)
            return User.from_db(db_user)

    async def authenticate_user(self, username_or_handle: str, password: str) -> Optional[User]:
        with self.entrypoint_db.user as user_db:
            db_user = user_db.authenticate(username_or_handle, password)
            return User.from_db(db_user)

    async def update_user(self, user_id: int, **kwargs) -> User:
        with self.entrypoint_db.user as user_db:
            if "password" in kwargs and kwargs["password"]:
                kwargs["hashed_password"] = UserDB.get_password_hash(kwargs.pop("password"))
            db_user = user_db.update(user_id, **kwargs)
            return User.from_db(db_user)

    async def delete_user(self, user_id: int) -> None:
        with self.entrypoint_db.user as user_db:
            user_db.delete(user_id)

    async def list_users(self, limit: int = 10, page: int = 0, **kwargs) -> list[User]:
        with self.entrypoint_db.user as user_db:
            users = user_db.list(limit=limit, **kwargs)
            return [User.from_db(user) for user in page_limit_query(users, limit=limit, page=page)]
