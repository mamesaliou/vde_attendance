from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import date, datetime, timedelta
from typing import List, Optional, Dict
from ..models.models import Attendance, Student, Class
from ..schemas.schemas import AttendanceCreate, AttendanceUpdate

class AttendanceService:
    @staticmethod
    def record_attendance(db: Session, attendance_data: AttendanceCreate) -> Optional[Attendance]:
        # Vérifier si l'enregistrement existe déjà
        existing = db.query(Attendance).filter(
            Attendance.student_id == attendance_data.student_id,
            Attendance.class_id == attendance_data.class_id,
            Attendance.date == attendance_data.date
        ).first()
        
        if existing:
            return None
        
        db_attendance = Attendance(**attendance_data.dict())
        db.add(db_attendance)
        db.commit()
        db.refresh(db_attendance)
        return db_attendance
    
    @staticmethod
    def record_bulk_attendance(db: Session, attendances_data: List[AttendanceCreate]) -> Dict:
        results = {
            "successful": 0,
            "failed": 0,
            "errors": []
        }
        
        for attendance_data in attendances_data:
            try:
                result = AttendanceService.record_attendance(db, attendance_data)
                if result:
                    results["successful"] += 1
                else:
                    results["failed"] += 1
                    results["errors"].append({
                        "student_id": attendance_data.student_id,
                        "date": attendance_data.date,
                        "error": "Attendance already exists"
                    })
            except Exception as e:
                results["failed"] += 1
                results["errors"].append({
                    "student_id": attendance_data.student_id,
                    "date": attendance_data.date,
                    "error": str(e)
                })
        
        return results
    
    @staticmethod
    def get_attendance_by_date_class(db: Session, class_id: int, attendance_date: date) -> List[Dict]:
        students = db.query(Student).filter(Student.class_id == class_id).all()
        attendances = db.query(Attendance).filter(
            Attendance.class_id == class_id,
            Attendance.date == attendance_date
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
    
    @staticmethod
    def get_student_attendance_history(db: Session, student_id: int, start_date: date, end_date: date) -> List[Attendance]:
        return db.query(Attendance).filter(
            Attendance.student_id == student_id,
            Attendance.date >= start_date,
            Attendance.date <= end_date
        ).order_by(Attendance.date.desc()).all()
    
    @staticmethod
    def get_daily_attendance_stats(db: Session, class_id: int, attendance_date: date) -> Dict:
        total_students = db.query(Student).filter(Student.class_id == class_id).count()
        present_count = db.query(Attendance).filter(
            Attendance.class_id == class_id,
            Attendance.date == attendance_date,
            Attendance.present == True
        ).count()
        
        absent_count = total_students - present_count
        attendance_rate = (present_count / total_students * 100) if total_students > 0 else 0
        
        return {
            "date": attendance_date,
            "class_id": class_id,
            "total_students": total_students,
            "present_count": present_count,
            "absent_count": absent_count,
            "attendance_rate": round(attendance_rate, 2)
        }
    
    @staticmethod
    def get_monthly_report(db: Session, class_id: int, year: int, month: int) -> Dict:
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)
        
        # Statistiques générales
        total_days = (end_date - start_date).days + 1
        daily_stats = []
        
        current_date = start_date
        while current_date <= end_date:
            stats = AttendanceService.get_daily_attendance_stats(db, class_id, current_date)
            daily_stats.append(stats)
            current_date += timedelta(days=1)
        
        # Élèves les plus absents
        absent_students = db.query(
            Student, 
            func.count(Attendance.id).label('absent_days')
        ).join(
            Attendance, 
            and_(
                Attendance.student_id == Student.id,
                Attendance.date >= start_date,
                Attendance.date <= end_date,
                Attendance.present == False
            )
        ).filter(
            Student.class_id == class_id
        ).group_by(Student.id).order_by(func.count(Attendance.id).desc()).limit(5).all()
        
        most_absent = [
            {
                "student_id": student.id,
                "first_name": student.first_name,
                "last_name": student.last_name,
                "absent_days": absent_days
            }
            for student, absent_days in absent_students
        ]
        
        # Taux de présence moyen
        total_attendance_rate = sum(day['attendance_rate'] for day in daily_stats if day['total_students'] > 0)
        days_with_data = len([day for day in daily_stats if day['total_students'] > 0])
        average_attendance = total_attendance_rate / days_with_data if days_with_data > 0 else 0
        
        return {
            "month": f"{year}-{month:02d}",
            "class_id": class_id,
            "total_days": total_days,
            "days_with_data": days_with_data,
            "average_attendance": round(average_attendance, 2),
            "daily_stats": daily_stats,
            "most_absent_students": most_absent
        }