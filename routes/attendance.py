from flask import Blueprint, render_template
from models.attendance import Attendance
from utils.auth import login_required

attendance_bp = Blueprint(
    "attendance",
    __name__,
    url_prefix="/attendance"
)


@attendance_bp.route("/")
@login_required
def attendance():

    records = Attendance.query.order_by(
        Attendance.scan_date.desc(),
        Attendance.scan_time.desc()
    ).all()

    return render_template(
        "attendance/attendance.html",
        attendance=records
    )