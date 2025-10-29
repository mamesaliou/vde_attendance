from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional, List

# Student Schemas
class StudentBase(BaseModel):
    first_name: str
    last_name: str
    email: Optional[str] = None  # Changé de EmailStr à str
    class_id: Optional[int] = None

class StudentCreate(StudentBase):
    pass

class StudentUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None  # Changé de EmailStr à str
    class_id: Optional[int] = None

class Student(StudentBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Class Schemas
class ClassBase(BaseModel):
    name: str
    grade: str
    teacher_name: Optional[str] = None

class ClassCreate(ClassBase):
    pass

class ClassUpdate(BaseModel):
    name: Optional[str] = None
    grade: Optional[str] = None
    teacher_name: Optional[str] = None

class Class(ClassBase):
    id: int
    created_at: datetime
    students: List[Student] = []
    
    class Config:
        from_attributes = True

# Attendance Schemas
class AttendanceBase(BaseModel):
    student_id: int
    class_id: int
    date: date
    present: bool = True
    reason: Optional[str] = None

class AttendanceCreate(AttendanceBase):
    pass

class AttendanceUpdate(BaseModel):
    present: Optional[bool] = None
    reason: Optional[str] = None

class Attendance(AttendanceBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class AttendanceWithStudent(Attendance):
    student: Student

# Response Schemas
class PaginatedResponse(BaseModel):
    items: List
    total: int
    page: int
    size: int
    pages: int