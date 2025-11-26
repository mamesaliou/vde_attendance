from sqlalchemy.ext.declarative import declarative_base

# metadata = MetaData(schema=os.getenv("DB_SCHEMA") or Constants().db_schema)
Base = declarative_base()