from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Utiliser SQLite pour les tests, PostgreSQL pour la production
if os.getenv("TESTING", "False").lower() == "true":
    DATABASE_URL = "sqlite:///./test.db"
else:
    DATABASE_URL = os.getenv(
        "DATABASE_URL", 
        "postgresql://user:password@db:5432/school_attendance"
    )

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Importer tous les modèles pour qu'ils soient reconnus par SQLAlchemy
# from ..models.models import Class, Student, Attendance
# from ..auth.model import User

# Créer les tables seulement si ce n'est pas un import de test
if not os.getenv("TESTING"):
    Base.metadata.create_all(bind=engine)