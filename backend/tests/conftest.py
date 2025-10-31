import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from datetime import datetime, date

# Définir l'environnement de test AVANT les imports
os.environ["TESTING"] = "True"

from app.main import app
from app.database.database import Base, get_db
from app.auth.dependencies import get_password_hash
from app.models.models import Class, Student, Attendance
from backend.app.auth.models.model import User, UserRole

# Base de données de test SQLite en mémoire
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function")
def test_db():
    """Crée une base de données de test pour chaque test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(test_db):
    """Client de test FastAPI"""
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture
def sample_teacher(test_db):
    """Crée un enseignant de test"""
    teacher = User(
        email="teacher@test.com",
        username="testteacher",
        hashed_password=get_password_hash("Teacher123!"),
        first_name="Test",
        last_name="Teacher",
        role=UserRole.teacher,
        is_active=True
    )
    test_db.add(teacher)
    test_db.commit()
    test_db.refresh(teacher)
    return teacher

@pytest.fixture
def sample_admin(test_db):
    """Crée un admin de test"""
    admin = User(
        email="admin@test.com",
        username="testadmin",
        hashed_password=get_password_hash("Admin123!"),
        first_name="Test",
        last_name="Admin",
        role=UserRole.admin,
        is_active=True
    )
    test_db.add(admin)
    test_db.commit()
    test_db.refresh(admin)
    return admin

@pytest.fixture
def sample_class(test_db, sample_teacher):
    """Crée une classe de test"""
    class_ = Class(
        name="Test Class",
        grade="CM1",
        teacher_id=sample_teacher.id
    )
    test_db.add(class_)
    test_db.commit()
    test_db.refresh(class_)
    return class_

@pytest.fixture
def sample_student(test_db, sample_class):
    """Crée un étudiant de test"""
    student = Student(
        first_name="John",
        last_name="Doe",
        email="john.doe@test.com",
        class_id=sample_class.id
    )
    test_db.add(student)
    test_db.commit()
    test_db.refresh(student)
    return student

@pytest.fixture
def auth_headers(client, sample_teacher):
    """Retourne les headers d'authentification pour un enseignant"""
    login_data = {
        "username": sample_teacher.username,
        "password": "Teacher123!"
    }
    response = client.post("/api/auth/login", json=login_data)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def admin_headers(client, sample_admin):
    """Retourne les headers d'authentification pour un admin"""
    login_data = {
        "username": sample_admin.username,
        "password": "Admin123!"
    }
    response = client.post("/api/auth/login", json=login_data)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}