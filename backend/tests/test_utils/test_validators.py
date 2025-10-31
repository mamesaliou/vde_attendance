import pytest
from app.auth.dependencies import get_password_strength

class TestPasswordValidators:
    def test_password_strength_strong(self):
        """Test un mot de passe fort"""
        result = get_password_strength("StrongPass123!")
        
        assert result["strength"] == "strong"
        assert result["score"] >= 5
        assert result["valid"] == True

    def test_password_strength_weak(self):
        """Test un mot de passe faible"""
        result = get_password_strength("weak")
        
        assert result["strength"] == "weak"
        assert result["score"] < 3
        assert result["valid"] == False

    def test_password_too_long(self):
        """Test un mot de passe trop long"""
        long_password = "a" * 100
        result = get_password_strength(long_password)
        
        assert result["checks"]["not_too_long"] == False
        assert result["valid"] == False