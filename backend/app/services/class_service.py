from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from ..models.models import Class, Student
from ..schemas.schemas import ClassCreate, ClassUpdate

class ClassService:
    @staticmethod
    def get_class(db: Session, class_id: int) -> Optional[Class]:
        return db.query(Class).filter(Class.id == class_id).first()
    
    @staticmethod
    def get_classes(db: Session, skip: int = 0, limit: int = 100) -> List[Class]:
        classes = db.query(Class).offset(skip).limit(limit).all()
        
        # Ajouter le compte d'élèves
        for class_ in classes:
            class_.student_count = db.query(Student).filter(
                Student.class_id == class_.id
            ).count()
        
        return classes
    
    @staticmethod
    def create_class(db: Session, class_data: ClassCreate) -> Class:
        db_class = Class(**class_data.dict())
        db.add(db_class)
        db.commit()
        db.refresh(db_class)
        return db_class
    
    @staticmethod
    def update_class(db: Session, class_id: int, class_data: ClassUpdate) -> Optional[Class]:
        db_class = db.query(Class).filter(Class.id == class_id).first()
        if not db_class:
            return None
        
        for field, value in class_data.dict(exclude_unset=True).items():
            setattr(db_class, field, value)
        
        db.commit()
        db.refresh(db_class)
        return db_class
    
    @staticmethod
    def delete_class(db: Session, class_id: int) -> bool:
        db_class = db.query(Class).filter(Class.id == class_id).first()
        if not db_class:
            return False
        
        db.delete(db_class)
        db.commit()
        return True