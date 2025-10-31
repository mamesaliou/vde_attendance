from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Dict
from ..services.student_service import StudentService
from ..models.models import Attendance
from ..database.database import get_db
from ..services.attendance_service import AttendanceService

router = APIRouter()

@router.get("/monthly")
def get_monthly_report(
    class_id: int,
    year: int = Query(..., description="Année (ex: 2024)"),
    month: int = Query(..., description="Mois (1-12)"),
    db: Session = Depends(get_db)
):
    if month < 1 or month > 12:
        raise HTTPException(status_code=400, detail="Le mois doit être entre 1 et 12")
    
    if year < 2000 or year > 2100:
        raise HTTPException(status_code=400, detail="L'année doit être entre 2000 et 2100")
    
    return AttendanceService.get_monthly_report(db, class_id, year, month)

@router.get("/student/{student_id}/summary")
def get_student_summary(
    student_id: int,
    db: Session = Depends(get_db)
):  
    student = StudentService.get_student(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    attendance_rate = StudentService.get_student_attendance_rate(db, student_id)
    
    # Dernières absences
    recent_absences = db.query(Attendance).filter(
        Attendance.student_id == student_id,
        Attendance.present == False
    ).order_by(Attendance.date.desc()).limit(5).all()
    
    return {
        "student": student,
        "attendance_rate": attendance_rate,
        "recent_absences": [
            {
                "date": absence.date,
                "reason": absence.reason
            }
            for absence in recent_absences
        ]
    }