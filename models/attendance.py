from datetime import datetime
from models import db


class Attendance(db.Model):

    __tablename__ = "attendance"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("students.id"),
        nullable=False
    )

    scan_date = db.Column(
        db.Date,
        default=lambda: datetime.now().date()
    )

    scan_time = db.Column(
        db.DateTime,
        default=datetime.now
    )

    scan_type = db.Column(
        db.String(10),
        nullable=False
    )   # ENTRY or EXIT

    student = db.relationship(
        "Student",
        backref="attendance_records"
    )

    def __repr__(self):
        return f"<Attendance {self.student_id} {self.scan_type}>"