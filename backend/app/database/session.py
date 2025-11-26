from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings


class SqlAlchemySession:
    def __init__(self):
        database = settings.CONNECTION_STRING
        engine = create_engine(database, pool_pre_ping=True, max_overflow=20, pool_size=10)
        self.session_maker = sessionmaker(bind=engine)

    def __del__(self):
        self.session_maker().close()
        del self