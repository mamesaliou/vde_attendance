from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr
from app.database.models.user import UserDB


class User(BaseModel):
    id: int
    email: EmailStr
    username: str
    first_name: str
    last_name: str
    role: str
    handle: str
    hashed_password: str
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    code: Optional[str] = None

    @classmethod
    def from_db(cls, user: UserDB):
        return User(
            id=user.id,
            username=user.username,
            handle=user.handle,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            hashed_password=user.hashed_password,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
            created_at=user.created_at,
            updated_at=user.updated_at,
            code=user.code,
            role=user.role
        )