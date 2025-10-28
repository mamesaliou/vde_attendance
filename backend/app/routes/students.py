from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from .. schemas import schemas 
from .. models import models
from .. database.database import get_db

router = APIRouter()

@router.post("/", response_model=schemas.Student)
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):
    db_student = models.Student(**student.dict())
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

@router.get("/", response_model=List[schemas.Student])
def read_students(
    skip: int = 0,
    limit: int = 100,
    class_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Student)
    if class_id:
        query = query.filter(models.Student.class_id == class_id)
    return query.offset(skip).limit(limit).all()

@router.get("/{student_id}", response_model=schemas.Student)
def read_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@router.put("/{student_id}", response_model=schemas.Student)
def update_student(student_id: int, student: schemas.StudentUpdate, db: Session = Depends(get_db)):
    db_student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if db_student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    
    for field, value in student.dict(exclude_unset=True).items():
        setattr(db_student, field, value)
    
    db.commit()
    db.refresh(db_student)
    return db_student

@router.delete("/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    
    db.delete(student)
    db.commit()
    return {"message": "Student deleted successfully"}