from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, ForeignKey, Text, func, UniqueConstraint
from sqlalchemy.orm import relationship
from ..database.database import Base

class Class(Base):
    __tablename__ = "classes"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    grade = Column(String(50), nullable=False)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # nullable=True temporairement
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Spécifier explicitement la clé étrangère
    teacher = relationship("User", back_populates="taught_classes", foreign_keys=[teacher_id])
    students = relationship("Student", back_populates="class_", cascade="all, delete-orphan")
    attendances = relationship("Attendance", back_populates="class_")

class Student(Base):
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True)
    class_id = Column(Integer, ForeignKey("classes.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Spécifier explicitement les clés étrangères
    class_ = relationship("Class", back_populates="students", foreign_keys=[class_id])
    attendances = relationship("Attendance", back_populates="student")
    user = relationship("User", back_populates="student_record", foreign_keys=[user_id])

class Attendance(Base):
    __tablename__ = "attendances"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False, index=True)
    present = Column(Boolean, default=True)
    reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Spécifier explicitement les clés étrangères
    student = relationship("Student", back_populates="attendances", foreign_keys=[student_id])
    class_ = relationship("Class", back_populates="attendances", foreign_keys=[class_id])
    
    __table_args__ = (
        UniqueConstraint('student_id', 'class_id', 'date', name='unique_attendance'),
    )