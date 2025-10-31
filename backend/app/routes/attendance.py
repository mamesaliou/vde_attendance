from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date
from typing import List, Optional
from ..database.database import get_db
from ..schemas.schemas import Attendance, AttendanceCreate, AttendanceUpdate, AttendanceWithStudent
from ..services.attendance_service import AttendanceService

router = APIRouter()

@router.post("/", response_model=Attendance)
def create_attendance(attendance: AttendanceCreate, db: Session = Depends(get_db)):
    result = AttendanceService.record_attendance(db, attendance)
    if result is None:
        raise HTTPException(status_code=400, detail="Attendance already exists for this date")
    return result

@router.post("/bulk")
def create_bulk_attendance(attendances: List[AttendanceCreate], db: Session = Depends(get_db)):
    results = AttendanceService.record_bulk_attendance(db, attendances)
    return results

@router.get("/", response_model=List[AttendanceWithStudent])
def read_attendances(
    class_id: Optional[int] = None,
    student_id: Optional[int] = None,
    attendance_date: Optional[date] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    # Implémentation de la recherche filtrée
    query = db.query(Attendance).join(Attendance.student)
    
    if class_id:
        query = query.filter(Attendance.class_id == class_id)
    if student_id:
        query = query.filter(Attendance.student_id == student_id)
    if attendance_date:
        query = query.filter(Attendance.date == attendance_date)
    
    attendances = query.offset(skip).limit(limit).all()
    
    return [AttendanceWithStudent(
        **attendance.__dict__,
        student=attendance.student
    ) for attendance in attendances]

@router.get("/class/{class_id}/date/{attendance_date}")
def read_class_attendance(class_id: int, attendance_date: date, db: Session = Depends(get_db)):
    return AttendanceService.get_attendance_by_date_class(db, class_id, attendance_date)

@router.get("/student/{student_id}/history")
def read_student_attendance_history(
    student_id: int,
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db)
):
    return AttendanceService.get_student_attendance_history(db, student_id, start_date, end_date)

@router.get("/stats/daily")
def get_daily_stats(class_id: int, attendance_date: date, db: Session = Depends(get_db)):
    return AttendanceService.get_daily_attendance_stats(db, class_id, attendance_date)

@router.put("/{attendance_id}", response_model=Attendance)
def update_attendance(attendance_id: int, attendance: AttendanceUpdate, db: Session = Depends(get_db)):
    db_attendance = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    if db_attendance is None:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    
    for field, value in attendance.dict(exclude_unset=True).items():
        setattr(db_attendance, field, value)
    
    db.commit()
    db.refresh(db_attendance)
    return db_attendance