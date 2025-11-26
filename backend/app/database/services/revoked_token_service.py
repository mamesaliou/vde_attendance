from datetime import datetime, timezone

from sqlalchemy.exc import NoResultFound
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed

from app.tools.exceptions import DbOperationalError
from app.database.models.revoked_token import RevokedToken as RevokedTokenDB
from app.database.services._db_abstract_service import Service

class RevokedTokenService(Service):
    def __init__(self, session):
        Service.__init__(self, session=session, table=RevokedTokenDB)

    @retry(reraise=True, retry=retry_if_exception_type(DbOperationalError), wait=wait_fixed(2),
           stop=stop_after_attempt(2))
    def create(self, jti: str, expires_at: datetime, revoked_by: str, device_info: str = None):
        try:
            return self.get_by_jti(jti)
        except NoResultFound:
            revoked = RevokedTokenDB(
                jti=jti,
                expires_at=expires_at,
                revoked_by=revoked_by,
                device_info=device_info
            )
            self.insert(revoked)
            return self.get_by_jti(jti)

    @retry(reraise=True, retry=retry_if_exception_type(DbOperationalError), wait=wait_fixed(2),
           stop=stop_after_attempt(2))
    def get_by_jti(self, jti: str):
        return self.list(jti=jti).one()

    @retry(reraise=True, retry=retry_if_exception_type(DbOperationalError), wait=wait_fixed(2),
           stop=stop_after_attempt(2))
    def cleanup_expired(self):
        now = datetime.now(timezone.utc)
        self.list(expires_at=now).delete()
