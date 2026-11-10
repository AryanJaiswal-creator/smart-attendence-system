from flask import Blueprint, jsonify
from models.attendance import Attendance
from utils.auth import login_required

activity_bp = Blueprint(
    "activity",
    __name__,
    url_prefix="/activity"
)


@activity_bp.route("/recent")
@login_required
def recent_activity():

    records = Attendance.query.order_by(
        Attendance.scan_time.desc()
    ).limit(10).all()

    data = []

    for record in records:

        data.append({

    "student": record.student.name,

    "class": record.student.student_class,

    "section": record.student.section,

    "code": record.student.student_code,

    "photo": record.student.photo,

    "type": record.scan_type,

    "time": record.scan_time.strftime("%H:%M:%S")

})

    return jsonify(data)