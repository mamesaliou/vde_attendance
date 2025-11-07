import pytest

class TestAuthRoutes:
    def test_login_success(self, client, sample_teacher):
        """Test la connexion réussie"""
        login_data = {
            "username": sample_teacher.username,
            "password": "Teacher123!"
        }
        
        response = client.post("/api/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == sample_teacher.email

    def test_login_wrong_password(self, client, sample_teacher):
        """Test la connexion avec mauvais mot de passe"""
        login_data = {
            "username": sample_teacher.username,
            "password": "WrongPassword!"
        }
        
        response = client.post("/api/auth/login", json=login_data)
        
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]

    # def test_register_success(self, client, sample_class):
    #     """Test l'inscription réussie"""
    #     register_data = {
    #         "email": "new@test.com",
    #         "username": "newuser",
    #         "password": "NewUser123!",
    #         "first_name": "New",
    #         "last_name": "User",
    #         "role": "student",
    #         "class_id": sample_class.id
    #     }
        
    #     response = client.post("/api/auth/register", json=register_data)
        
    #     assert response.status_code == 200
    #     data = response.json()
    #     assert data["email"] == "new@test.com"
    #     assert data["username"] == "newuser"

    def test_get_current_user(self, client, auth_headers, sample_teacher):
        """Test la récupération de l'utilisateur courant"""
        response = client.get("/api/auth/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == sample_teacher.email
        assert data["username"] == sample_teacher.username

    def test_logout_success_bt(self, client, auth_headers):
        """Test de déconnexion réussie"""
        response = client.post("api/auth/logoutbt", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["message"] == "Déconnexion réussie"
    
    def test_logout_success_bc(self, client, auth_headers):
        """Test de déconnexion réussie"""
        response = client.post("api/auth/logoutbc", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["message"] == "Déconnexion réussie"

    def test_logout_without_token(self, client):
        """Test de déconnexion sans token"""
        response = client.post("api/auth/logoutbt", headers="")
        assert response.status_code == 403  # Ou 401 selon votre configuration

    def test_logout_with_blacklisted_token(self, client, auth_headers):
        """Test avec un token blacklisté"""
        # Premier logout - devrait réussir
        response1 = client.post("api/auth/logoutbt", headers=auth_headers)
        assert response1.status_code == 200
        assert response1.json()["message"] == "Déconnexion réussie"
        
        # Deuxième tentative avec le même token - devrait échouer avec 401
        response2 = client.post("api/auth/logoutbt", headers=auth_headers)
        assert response2.status_code == 401  
        assert "revoked" in response2.json()["detail"]