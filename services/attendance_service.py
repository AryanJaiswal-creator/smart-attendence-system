from datetime import datetime, timedelta

from models import db
from models.student import Student
from models.attendance import Attendance


def mark_attendance(student_code):

    # Find student
    student = Student.query.filter_by(
        student_code=student_code
    ).first()

    if student is None:
        return "Student not found"

    # =========================================
    # Prevent duplicate scans within 5 seconds
    # =========================================
    last_scan = Attendance.query.filter_by(
        student_id=student.id
    ).order_by(
        Attendance.scan_time.desc()
    ).first()

    if last_scan:
        difference = datetime.now() - last_scan.scan_time

        if difference < timedelta(seconds=5):
            return "Please wait before scanning again."

    # Today's date
    today = datetime.now().date()

    # Count today's scans
    total_scans = Attendance.query.filter_by(
        student_id=student.id,
        scan_date=today
    ).count()

    # Alternate ENTRY / EXIT
    if total_scans % 2 == 0:
        scan_type = "ENTRY"
    else:
        scan_type = "EXIT"

    attendance = Attendance(
        student_id=student.id,
        scan_date=today,
        scan_time=datetime.now(),
        scan_type=scan_type
    )

    db.session.add(attendance)
    db.session.commit()

    return f"{student.name} {scan_type} Recorded"