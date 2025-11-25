from app.database.database import Database
from app.database.services.invitation_code_service import InvitationCodeService
from app.database.services.revoked_token_service import RevokedTokenService
from app.database.services.user_service import UserService


class EntryPointDb(Database):

    def __init__(self):
        super().__init__()

    @property
    def user(self):
        return UserService(session=self.session)

    @property
    def invitation_code(self):
        return InvitationCodeService(self.session)

    @property
    def revoked_token(self):
        return RevokedTokenService(self.session)
