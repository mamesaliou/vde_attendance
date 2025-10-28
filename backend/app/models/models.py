from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .. database.database import Base

class Student(Base):
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True)
    class_id = Column(Integer, ForeignKey("classes.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    class_ = relationship("Class", back_populates="students")
    attendances = relationship("Attendance", back_populates="student")

class Class(Base):
    __tablename__ = "classes"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    grade = Column(String(50), nullable=False)
    teacher_name = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    students = relationship("Student", back_populates="class_")
    attendances = relationship("Attendance", back_populates="class_")

class Attendance(Base):
    __tablename__ = "attendances"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    date = Column(Date, nullable=False)
    present = Column(Boolean, default=True)
    reason = Column(Text, nullable=True)  # For absences
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    student = relationship("Student", back_populates="attendances")
    class_ = relationship("Class", back_populates="attendances")