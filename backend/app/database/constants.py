from app.tools import Singleton


class Constants(metaclass=Singleton):
    def __init__(self):
        self.db_schema = "dbo"
