from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    email: EmailStr
    username: str
    first_name: str
    last_name: str
    role: str