import pytest

class TestStudentRoutes:
    def test_create_student_authenticated(self, client, auth_headers, sample_class):
        """Test la création d'étudiant avec authentification"""
        student_data = {
            "first_name": "Route",
            "last_name": "Test",
            "email": "route.test@example.com",
            "class_id": sample_class.id
        }
        
        response = client.post(
            "/api/students/", 
            json=student_data, 
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "Route"
        assert data["email"] == "route.test@example.com"

    def test_create_student_unauthenticated(self, client, sample_class):
        """Test la création d'étudiant sans authentification"""
        student_data = {
            "first_name": "Route",
            "last_name": "Test", 
            "email": "route.test@example.com",
            "class_id": sample_class.id
        }
        
        response = client.post("/api/students/", json=student_data)
        
        assert response.status_code == 403
        assert "Not authenticated" in response.json()["detail"]

    def test_get_students_authenticated(self, client, auth_headers, sample_student):
        """Test la récupération des étudiants avec authentification"""
        response = client.get("/api/students/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_get_student_by_id(self, client, auth_headers, sample_student):
        """Test la récupération d'un étudiant par ID"""
        response = client.get(
            f"/api/students/{sample_student.id}", 
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_student.id
        assert data["first_name"] == sample_student.first_name