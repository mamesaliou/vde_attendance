import pytest
from fastapi import HTTPException
from app.auth.service import AuthService
from app.auth.schema import UserCreate, UserLogin
from backend.app.auth.models.model import UserRole

class TestAuthService:
    def test_authenticate_user_success(self, test_db, sample_teacher):
        """Test l'authentification réussie"""
        user = AuthService.authenticate_user(
            test_db, 
            sample_teacher.username, 
            "Teacher123!"
        )
        
        assert user is not None
        assert user.id == sample_teacher.id
        assert user.email == sample_teacher.email

    def test_authenticate_user_wrong_password(self, test_db, sample_teacher):
        """Test l'authentification avec mauvais mot de passe"""
        user = AuthService.authenticate_user(
            test_db, 
            sample_teacher.username, 
            "WrongPassword!"
        )
        
        assert user is False

    def test_authenticate_user_not_found(self, test_db):
        """Test l'authentification avec utilisateur inexistant"""
        user = AuthService.authenticate_user(
            test_db, 
            "nonexistent", 
            "password"
        )
        
        assert user is False

    def test_register_user_success(self, test_db, sample_class):
        """Test l'enregistrement d'un nouvel utilisateur"""
        user_data = UserCreate(
            email="newuser@test.com",
            username="newuser",
            password="NewUser123!",
            first_name="New",
            last_name="User",
            role="student",
            class_id=sample_class.id
        )
        
        user = AuthService.register_user(test_db, user_data)
        
        assert user.id is not None
        assert user.email == "newuser@test.com"
        assert user.role == "student"

    def test_register_user_duplicate_email(self, test_db, sample_teacher):
        """Test l'enregistrement avec email existant"""
        user_data = UserCreate(
            email=sample_teacher.email,  # Email déjà existant
            username="differentuser",
            password="Password123!",
            first_name="Different",
            last_name="User",
            role="student",
            class_id=1
        )
        
        with pytest.raises(HTTPException) as exc_info:
            AuthService.register_user(test_db, user_data)
        
        assert exc_info.value.status_code == 400
        assert "Email already registered" in str(exc_info.value.detail)

    def test_register_user_weak_password(self, test_db):
        """Test l'enregistrement avec mot de passe faible"""
        # Ce test devrait échouer lors de la création de l'objet UserCreate
        # car la validation Pydantic se fait à l'instanciation
        with pytest.raises(ValueError) as exc_info:
            user_data = UserCreate(
                email="weak@test.com",
                username="weakuser",
                password="weak",  # Mot de passe trop faible
                first_name="Weak",
                last_name="User",
                role="student",
                class_id=1
            )
        
        assert "Le mot de passe doit contenir au moins 8 caractères" in str(exc_info.value)