import pytest
from backend.app.auth.models.model import User, UserRole

class TestUserModel:
    def test_create_user(self, test_db):
        """Test la création d'un utilisateur"""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashedpassword",
            first_name="Test",
            last_name="User",
            role=UserRole.student
        )
        
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        
        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.role == UserRole.student
        assert user.is_active == True

    def test_user_to_dict(self, sample_teacher):
        """Test la conversion user vers dict"""
        user_dict = sample_teacher.to_dict()
        
        assert user_dict["email"] == sample_teacher.email
        assert user_dict["username"] == sample_teacher.username
        assert user_dict["role"] == "teacher"
        assert "created_at" in user_dict

    def test_user_role_enum(self):
        """Test les valeurs de l'enum UserRole"""
        assert UserRole.student.value == "student"
        assert UserRole.teacher.value == "teacher"
        assert UserRole.admin.value == "admin"