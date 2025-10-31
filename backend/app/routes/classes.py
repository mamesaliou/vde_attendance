from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from ..database.database import get_db
from ..schemas.schemas import Class, ClassCreate, ClassUpdate, PaginatedResponse
from ..services.class_service import ClassService

router = APIRouter()

@router.post("/", response_model=Class)
def create_class(class_data: ClassCreate, db: Session = Depends(get_db)):
    return ClassService.create_class(db, class_data)

@router.get("/", response_model=List[Class])
def read_classes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return ClassService.get_classes(db, skip, limit)

@router.get("/{class_id}", response_model=Class)
def read_class(class_id: int, db: Session = Depends(get_db)):
    class_ = ClassService.get_class(db, class_id)
    if class_ is None:
        raise HTTPException(status_code=404, detail="Class not found")
    return class_

@router.put("/{class_id}", response_model=Class)
def update_class(class_id: int, class_data: ClassUpdate, db: Session = Depends(get_db)):
    class_ = ClassService.update_class(db, class_id, class_data)
    if class_ is None:
        raise HTTPException(status_code=404, detail="Class not found")
    return class_

@router.delete("/{class_id}")
def delete_class(class_id: int, db: Session = Depends(get_db)):
    success = ClassService.delete_class(db, class_id)
    if not success:
        raise HTTPException(status_code=404, detail="Class not found")
    return {"message": "Class deleted successfully"}