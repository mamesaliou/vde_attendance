from pydantic import BaseModel, validator
from datetime import date, datetime
from typing import Optional, List
import re

class ClassBase(BaseModel):
    name: str
    grade: str
    teacher_id: Optional[int] = None

class ClassCreate(ClassBase):
    @validator('name')
    def validate_name(cls, v):
        if len(v) < 2:
            raise ValueError('Le nom de la classe doit contenir au moins 2 caractères')
        return v

class ClassUpdate(BaseModel):
    name: Optional[str] = None
    grade: Optional[str] = None
    teacher_id: Optional[int] = None

class Class(ClassBase):
    id: int
    student_count: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class StudentBase(BaseModel):
    first_name: str
    last_name: str
    email: Optional[str] = None
    class_id: int

class StudentCreate(StudentBase):
    @validator('first_name', 'last_name')
    def validate_names(cls, v):
        if len(v) < 2:
            raise ValueError('Le nom doit contenir au moins 2 caractères')
        if not re.match(r'^[a-zA-ZÀ-ÿ\s\-]+$', v):
            raise ValueError('Le nom ne peut contenir que des lettres, espaces et tirets')
        return v
    
    @validator('email')
    def validate_email(cls, v):
        if v and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError('Format d\'email invalide')
        return v

class StudentUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    class_id: Optional[int] = None
    user_id: Optional[int] = None

class Student(StudentBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class StudentWithUser(Student):
    has_user_account: bool = False
    user: Optional[dict] = None

class StudentWithAttendance(Student):
    attendance_rate: Optional[float] = None
    user: Optional[dict] = None

class AttendanceBase(BaseModel):
    student_id: int
    class_id: int
    date: date
    present: bool = True
    reason: Optional[str] = None

class AttendanceCreate(AttendanceBase):
    @validator('reason')
    def validate_reason(cls, v, values):
        if not values.get('present') and not v:
            raise ValueError('Le motif est obligatoire pour une absence')
        return v

class AttendanceUpdate(BaseModel):
    present: Optional[bool] = None
    reason: Optional[str] = None

class Attendance(AttendanceBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class AttendanceWithStudent(Attendance):
    student: Student

class DailyAttendance(BaseModel):
    date: date
    class_id: int
    present_count: int
    absent_count: int
    attendance_rate: float

class MonthlyReport(BaseModel):
    month: str
    class_id: int
    total_days: int
    average_attendance: float
    most_absent_students: List[dict]

class PaginatedResponse(BaseModel):
    items: List
    total: int
    page: int
    size: int
    total_pages: int

