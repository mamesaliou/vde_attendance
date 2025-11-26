from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class RevokedToken(BaseModel):
    jti: str
    expires_at: datetime
    revoked_by: str
    device_info: Optional[str] = None

    @classmethod
    def from_db(cls, db_token):
        if not db_token:
            return None
        return cls(
            jti=db_token.jti,
            expires_at=db_token.expires_at,
            revoked_by=db_token.revoked_by,
            device_info=db_token.device_info
        )
