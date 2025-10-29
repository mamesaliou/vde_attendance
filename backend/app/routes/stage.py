from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. schemas import schemas
from .. models import models
from .. database.database import get_db

router = APIRouter()

@router.post("/", response_model=schemas.Class)
def create_class(class_: schemas.ClassCreate, db: Session = Depends(get_db)):
    db_class = models.Class(**class_.dict())
    db.add(db_class)
    db.commit()
    db.refresh(db_class)
    return db_class

@router.get("/", response_model=List[schemas.Class])
def read_classes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Class).offset(skip).limit(limit).all()

@router.get("/{class_id}", response_model=schemas.Class)
def read_class(class_id: int, db: Session = Depends(get_db)):
    class_ = db.query(models.Class).filter(models.Class.id == class_id).first()
    if class_ is None:
        raise HTTPException(status_code=404, detail="Class not found")
    return class_

@router.put("/{class_id}", response_model=schemas.Class)
def update_class(class_id: int, class_: schemas.ClassUpdate, db: Session = Depends(get_db)):
    db_class = db.query(models.Class).filter(models.Class.id == class_id).first()
    if db_class is None:
        raise HTTPException(status_code=404, detail="Class not found")
    
    for field, value in class_.dict(exclude_unset=True).items():
        setattr(db_class, field, value)
    
    db.commit()
    db.refresh(db_class)
    return db_class

@router.delete("/{class_id}")
def delete_class(class_id: int, db: Session = Depends(get_db)):
    class_ = db.query(models.Class).filter(models.Class.id == class_id).first()
    if class_ is None:
        raise HTTPException(status_code=404, detail="Class not found")
    
    db.delete(class_)
    db.commit()
    return {"message": "Class deleted successfully"}