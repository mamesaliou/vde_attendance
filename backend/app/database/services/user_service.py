from typing import Optional, Union, Iterable, Any

from sqlalchemy import func
from sqlalchemy.exc import NoResultFound
from tenacity import retry_if_exception_type, wait_fixed, stop_after_attempt, retry

from app.database.models.base import Base
from app.database.models.user import UserDB
from app.database.services._db_abstract_service import Service
from app.tools.exceptions import DbOperationalError


class UserService(Service):

    def __init__(self, session):
        Service.__init__(self, session=session, table=UserDB)

    def _filter(self, column_name: str, value: Optional[Union[str, Iterable]], table: Optional[Base] = None) -> Any:
        table = table or self._table
        column = getattr(table, column_name)
        if isinstance(value, Iterable) and not isinstance(value, str):
            return column.in_(value)
        elif column_name in ["username", "email", "handle", "first_name", "last_name"]:
            return func.lower(column) == value.lower()
        else:
            return column == value



    @retry(reraise=True, retry=retry_if_exception_type(DbOperationalError), wait=wait_fixed(2),
           stop=stop_after_attempt(2))
    def create(self, **kwargs):
        try:
            return self.get_by_username(kwargs["username"])
        except NoResultFound:
            try:
                return self.get_by_handle(kwargs["handle"])
            except NoResultFound:
                try:
                    return self.get_by_email(kwargs["email"])
                except NoResultFound:
                    user = UserDB(**kwargs)
        try:
            self.insert(user)
        except Exception:
            raise
        return self.get_by_username(user.username)

    @retry(reraise=True, retry=retry_if_exception_type(DbOperationalError), wait=wait_fixed(2),
           stop=stop_after_attempt(2))
    def get(self, entry_id: int):
        return self.list(id=entry_id).one()

    @retry(reraise=True, retry=retry_if_exception_type(DbOperationalError), wait=wait_fixed(2),
           stop=stop_after_attempt(2))
    def get_by_username(self, username: str):
        return self.list(username=username).one()

    @retry(reraise=True, retry=retry_if_exception_type(DbOperationalError), wait=wait_fixed(2),
           stop=stop_after_attempt(2))
    def get_by_handle(self, handle: str):
        return self.list(handle=handle).one()

    @retry(reraise=True, retry=retry_if_exception_type(DbOperationalError), wait=wait_fixed(2),
           stop=stop_after_attempt(2))
    def get_by_email(self, email: str):
        return self.list(email=email).one()

    @retry(reraise=True, retry=retry_if_exception_type(DbOperationalError), wait=wait_fixed(2),
           stop=stop_after_attempt(2))
    def get_user(self, **kwargs):
        return self.list(**kwargs).one()

    def authenticate(self, username: str, password: str) -> Optional[UserDB]:
        try:
            user = self.get_by_username(username)
            if user.verify_password(password):
                return user
        except NoResultFound:
            try:
                user = self.get_by_handle(username)
                if user.verify_password(password):
                    return user
            except NoResultFound:
                pass
        return None
