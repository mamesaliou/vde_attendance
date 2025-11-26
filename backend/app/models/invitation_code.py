from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class InvitationCode(BaseModel):
    code: str
    expires_at: datetime
    created_by: str
    is_superuser: bool
    used_at: Optional[datetime]

    @classmethod
    def from_db(cls, db_invitation):
        if not db_invitation:
            return None
        return cls(
            code=db_invitation.code,
            expires_at=db_invitation.expires_at,
            created_by=db_invitation.created_by,
            is_superuser=db_invitation.is_superuser,
            used_at=db_invitation.used_at
        )
