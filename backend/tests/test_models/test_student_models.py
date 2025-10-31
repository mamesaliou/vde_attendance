import pytest
from app.models.models import Student

class TestStudentModel:
    def test_create_student(self, test_db, sample_class):
        """Test la création d'un étudiant"""
        student = Student(
            first_name="Alice",
            last_name="Smith",
            email="alice.smith@test.com",
            class_id=sample_class.id
        )
        
        test_db.add(student)
        test_db.commit()
        test_db.refresh(student)
        
        assert student.id is not None
        assert student.first_name == "Alice"
        assert student.email == "alice.smith@test.com"
        assert student.class_id == sample_class.id

    def test_student_relationship(self, sample_student, sample_class):
        """Test la relation étudiant-classe"""
        assert sample_student.class_ == sample_class
        assert sample_student in sample_class.students