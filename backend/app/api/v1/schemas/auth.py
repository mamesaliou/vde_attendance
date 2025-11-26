from pydantic import BaseModel, EmailStr, Field

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    refresh_token: str
    expires_at: int  # Timestamp Unix en secondes pour l'expiration du token d'accès

class TokenData(BaseModel):
    username: str | None = None

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    handle: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    is_active: bool = False
    is_superuser: bool = False

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    invitation_code: str | None = None

class UserInDB(UserBase):
    hashed_password: str

class User(UserBase):
    id: int

    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    username: str
    password: str