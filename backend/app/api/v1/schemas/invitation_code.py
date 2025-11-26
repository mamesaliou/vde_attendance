from datetime import datetime
from pydantic import BaseModel


class InvitationCodeCreate(BaseModel):
    expires_in_days: int = 7
    is_superuser: bool = False


class InvitationCodeResponse(BaseModel):
    code: str
    expires_at: datetime
    is_superuser: bool
