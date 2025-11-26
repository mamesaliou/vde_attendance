from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime
from app.database.models.base import Base

class RevokedToken(Base):
    __tablename__ = "revoked_tokens"

    jti = Column(String(36), primary_key=True)
    revoked_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime, nullable=False)
    revoked_by = Column(String, nullable=False)
    device_info = Column(String, nullable=True)
