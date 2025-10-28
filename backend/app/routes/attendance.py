from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date
from typing import List, Optional
from .. schemas import schemas
from .. models import models
from .. database.database import get_db

router = APIRouter()

@router.post("/", response_model=schemas.Attendance)
def create_attendance(attendance: schemas.AttendanceCreate, db: Session = Depends(get_db)):
    # Check if student exists
    student = db.query(models.Student).filter(models.Student.id == attendance.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Check if class exists
    class_ = db.query(models.Class).filter(models.Class.id == attendance.class_id).first()
    if not class_:
        raise HTTPException(status_code=404, detail="Class not found")
    
    # Check if attendance already exists for this student/date/class
    existing = db.query(models.Attendance).filter(
        models.Attendance.student_id == attendance.student_id,
        models.Attendance.class_id == attendance.class_id,
        models.Attendance.date == attendance.date
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Attendance already recorded for this date")
    
    db_attendance = models.Attendance(**attendance.dict())
    db.add(db_attendance)
    db.commit()
    db.refresh(db_attendance)
    return db_attendance

@router.get("/", response_model=List[schemas.AttendanceWithStudent])
def read_attendances(
    class_id: Optional[int] = None,
    student_id: Optional[int] = None,
    attendance_date: Optional[date] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(models.Attendance).join(models.Student)
    
    if class_id:
        query = query.filter(models.Attendance.class_id == class_id)
    if student_id:
        query = query.filter(models.Attendance.student_id == student_id)
    if attendance_date:
        query = query.filter(models.Attendance.date == attendance_date)
    
    return query.offset(skip).limit(limit).all()

@router.get("/class/{class_id}/date/{attendance_date}")
def read_class_attendance(class_id: int, attendance_date: date, db: Session = Depends(get_db)):
    """Get attendance for all students in a class on a specific date"""
    # Get all students in the class
    students = db.query(models.Student).filter(models.Student.class_id == class_id).all()
    
    # Get existing attendance records
    attendances = db.query(models.Attendance).filter(
        models.Attendance.class_id == class_id,
        models.Attendance.date == attendance_date
    ).all()
    
    attendance_dict = {att.student_id: att for att in attendances}
    
    result = []
    for student in students:
        attendance = attendance_dict.get(student.id)
        result.append({
            "student": student,
            "attendance": attendance,
            "present": attendance.present if attendance else None,
            "reason": attendance.reason if attendance else None
        })
    
    return result

@router.put("/{attendance_id}", response_model=schemas.Attendance)
def update_attendance(attendance_id: int, attendance: schemas.AttendanceUpdate, db: Session = Depends(get_db)):
    db_attendance = db.query(models.Attendance).filter(models.Attendance.id == attendance_id).first()
    if db_attendance is None:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    
    for field, value in attendance.dict(exclude_unset=True).items():
        setattr(db_attendance, field, value)
    
    db.commit()
    db.refresh(db_attendance)
    return db_attendance

@router.post("/bulk")
def create_bulk_attendance(attendances: List[schemas.AttendanceCreate], db: Session = Depends(get_db)):
    """Create multiple attendance records at once"""
    created = []
    errors = []
    
    for attendance in attendances:
        try:
            db_attendance = models.Attendance(**attendance.dict())
            db.add(db_attendance)
            created.append(attendance)
        except Exception as e:
            errors.append({"student_id": attendance.student_id, "error": str(e)})
    
    db.commit()
    return {"created": len(created), "errors": errors}