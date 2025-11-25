from sqlalchemy.orm import sessionmaker

from app.database.session import SqlAlchemySession


class Database:

    def __init__(self):
        self.__database = None

    @property
    def session(self) -> sessionmaker:
        if self.__database is None:
            self.__database = SqlAlchemySession().session_maker()
        return self.__database