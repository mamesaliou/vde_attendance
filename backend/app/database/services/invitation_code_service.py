from datetime import datetime

from sqlalchemy.exc import NoResultFound
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed

from app.database.tools.exceptions import DbOperationalError
from app.database.models.invitation_code import InvitationCode as InvitationCodeDB
from app.database.services._db_abstract_service import Service

class InvitationCodeService(Service):
    def __init__(self, session):
        Service.__init__(self, session=session, table=InvitationCodeDB)

    @retry(reraise=True, retry=retry_if_exception_type(DbOperationalError), wait=wait_fixed(2),
           stop=stop_after_attempt(2))
    def create(self, code: str, expires_at: datetime, created_by: str, is_superuser: bool = False):
        try:
            return self.get_by_code(code)
        except NoResultFound:
            invitation = InvitationCodeDB(
                code=code,
                expires_at=expires_at,
                created_by=created_by,
                is_superuser=is_superuser
            )
            self.insert(invitation)
            return self.get_by_code(code)

    @retry(reraise=True, retry=retry_if_exception_type(DbOperationalError), wait=wait_fixed(2),
           stop=stop_after_attempt(2))
    def get_by_code(self, code: str):
        return self.list(code=code).one()

    @retry(reraise=True, retry=retry_if_exception_type(DbOperationalError), wait=wait_fixed(2),
           stop=stop_after_attempt(2))
    def get(self, entry_id):
        return self.get_by_code(entry_id)
