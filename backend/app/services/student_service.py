from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from ..models.models import Student, Attendance
from ..schemas.schemas import  StudentCreate, StudentUpdate
from ..auth.model import User

class StudentService:
    @staticmethod
    def get_student(db: Session, student_id: int) -> Optional[Student]:
        return db.query(Student).filter(Student.id == student_id).first()
    
    @staticmethod
    def get_students_by_class(db: Session, class_id: int, skip: int = 0, limit: int = 100) -> List[Student]:
        students = db.query(Student).filter(Student.class_id == class_id).offset(skip).limit(limit).all()
        
        # Ajouter les informations utilisateur
        for student in students:
            if student.user_id:
                user = db.query(User).filter(User.id == student.user_id).first()
                student.user = user
        
        return students
    
    @staticmethod
    def get_all_students(db: Session, skip: int = 0, limit: int = 100) -> List[Student]:
        return db.query(Student).offset(skip).limit(limit).all()
    
    @staticmethod
    def create_student(db: Session, student_data: StudentCreate) -> Student:
        # Vérifier si l'email existe déjà
        existing_student = db.query(Student).filter(Student.email == student_data.email).first()
        if existing_student:
            raise ValueError("Un étudiant avec cet email existe déjà")
        
        # Vérifier si un utilisateur avec cet email existe déjà
        existing_user = db.query(User).filter(User.email == student_data.email).first()
        if existing_user:
            # Lier l'étudiant à l'utilisateur existant
            student_data.user_id = existing_user.id
        
        db_student = Student(**student_data.dict())
        db.add(db_student)
        db.commit()
        db.refresh(db_student)
        return db_student
    
    @staticmethod
    def update_student(db: Session, student_id: int, student_data: StudentUpdate) -> Optional[Student]:
        db_student = db.query(Student).filter(Student.id == student_id).first()
        if not db_student:
            return None
        
        for field, value in student_data.dict(exclude_unset=True).items():
            setattr(db_student, field, value)
        
        db.commit()
        db.refresh(db_student)
        return db_student
    
    @staticmethod
    def delete_student(db: Session, student_id: int) -> bool:
        db_student = db.query(Student).filter(Student.id == student_id).first()
        if not db_student:
            return False
        
        db.delete(db_student)
        db.commit()
        return True
    
    @staticmethod
    def link_student_to_user(db: Session, student_id: int, user_id: int) -> bool:
        """Lie un étudiant à un compte utilisateur"""
        db_student = db.query(Student).filter(Student.id == student_id).first()
        if not db_student:
            return False
        
        db_student.user_id = user_id
        db.commit()
        return True
    
    @staticmethod
    def get_students_without_account(db: Session, class_id: Optional[int] = None) -> List[Student]:
        """Récupère les étudiants sans compte utilisateur"""
        query = db.query(Student).filter(Student.user_id.is_(None))
        
        if class_id:
            query = query.filter(Student.class_id == class_id)
        
        return query.all()
    
    @staticmethod
    def get_student_attendance_rate(db: Session, student_id: int) -> float:
        total_days = db.query(Attendance).filter(
            Attendance.student_id == student_id
        ).count()
        
        if total_days == 0:
            return 0.0
        
        present_days = db.query(Attendance).filter(
            Attendance.student_id == student_id,
            Attendance.present == True
        ).count()
        
        return (present_days / total_days) * 100