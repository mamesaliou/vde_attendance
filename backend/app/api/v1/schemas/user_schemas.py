from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
from enum import Enum
from typing import Optional
from datetime import datetime
import re

class UserRole(Enum):
    student = "student"
    teacher = "teacher"
    admin = "admin"

class UserBase(BaseModel):
    email: EmailStr
    username: str
    first_name: str
    last_name: str
    role: str

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    first_name: str
    last_name: str
    role: str = "student"
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password too weak : the password must content less of 8 bit.')
        if not re.search(r'[A-Z]', v):
            raise ValueError('he password must content less of a uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('The password must content less of a lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('The password must content less of a digit')
        return v
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError("Le nom d'utilisateur doit contenir au moins 3 caractères")
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError("Le nom d'utilisateur ne peut contenir que des lettres, chiffres et underscores")
        return v

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    email: str
    username: str
    first_name: str
    last_name: str
    role: str
    is_active: bool
    created_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[int] = None
    role: Optional[str] = None