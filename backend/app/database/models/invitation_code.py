import datetime
from sqlalchemy import Column, String, DateTime, Boolean
from app.database.models.base import Base

class InvitationCode(Base):
    __tablename__ = "invitation_codes"

    code = Column(String(64), primary_key=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    expires_at = Column(DateTime, nullable=False)
    used_at = Column(DateTime, nullable=True)
    created_by = Column(String, nullable=False)
