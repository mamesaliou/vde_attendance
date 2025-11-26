from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class UserBase(BaseModel):
    username: str
    handle: str = Field(..., pattern="^@?[a-zA-Z0-9_]+$")
    is_active: bool = True
    is_superuser: bool = False


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    password: Optional[str] = Field(None, min_length=8)
    is_active: Optional[bool] = True


class UserInDB(UserBase):
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserResponse(UserInDB):
    class Config:
        from_attributes = True
