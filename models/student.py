from datetime import datetime
from models import db


class Student(db.Model):

    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)

    student_code = db.Column(db.String(20), unique=True, nullable=False)

    name = db.Column(db.String(100), nullable=False)

    student_class = db.Column(db.String(20), nullable=False)

    section = db.Column(db.String(10), nullable=False)

    roll_number = db.Column(db.String(20), nullable=False)

    father_name = db.Column(db.String(100))

    mother_name = db.Column(db.String(100))

    phone = db.Column(db.String(20))

    email = db.Column(db.String(100))

    address = db.Column(db.Text)

    qr_code = db.Column(db.String(255))

    photo = db.Column(db.String(255))

    status = db.Column(db.Boolean, default=True)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    def __repr__(self):
        return f"<Student {self.student_code}>"