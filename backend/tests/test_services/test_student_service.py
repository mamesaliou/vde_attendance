import pytest
from app.services.student_service import StudentService
from app.schemas.schemas import StudentCreate, StudentUpdate

class TestStudentService:
    def test_create_student_success(self, test_db, sample_class):
        """Test la création d'un étudiant"""
        student_data = StudentCreate(
            first_name="Test",
            last_name="Student",
            email="test.student@example.com",
            class_id=sample_class.id
        )
        
        student = StudentService.create_student(test_db, student_data)
        
        assert student.id is not None
        assert student.first_name == "Test"
        assert student.email == "test.student@example.com"

    def test_create_student_duplicate_email(self, test_db, sample_student):
        """Test la création avec email existant"""
        student_data = StudentCreate(
            first_name="Another",
            last_name="Student",
            email=sample_student.email,  # Email déjà existant
            class_id=sample_student.class_id
        )
        
        with pytest.raises(ValueError) as exc_info:
            StudentService.create_student(test_db, student_data)
        
        assert "Un étudiant avec cet email existe déjà" in str(exc_info.value)

    def test_get_students_by_class(self, test_db, sample_class, sample_student):
        """Test la récupération des étudiants par classe"""
        students = StudentService.get_students_by_class(
            test_db, sample_class.id
        )
        
        assert len(students) >= 1
        assert students[0].id == sample_student.id

    def test_update_student(self, test_db, sample_student):
        """Test la mise à jour d'un étudiant"""
        update_data = StudentUpdate(first_name="Updated")
        
        updated_student = StudentService.update_student(
            test_db, sample_student.id, update_data
        )
        
        assert updated_student is not None
        assert updated_student.first_name == "Updated"
        assert updated_student.last_name == sample_student.last_name

    def test_delete_student(self, test_db, sample_student):
        """Test la suppression d'un étudiant"""
        result = StudentService.delete_student(test_db, sample_student.id)
        
        assert result == True
        
        # Vérifier que l'étudiant n'existe plus
        deleted_student = StudentService.get_student(test_db, sample_student.id)
        assert deleted_student is None