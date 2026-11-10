from datetime import date

from flask import (
    Blueprint,
    render_template,
    session,
    redirect,
    url_for
)
from utils.auth import login_required

from models.student import Student
from models.attendance import Attendance
from services.system_state import system_state


dashboard_bp = Blueprint(
    "dashboard",
    __name__
)


@dashboard_bp.route("/dashboard")
@login_required
def dashboard():

    today = date.today()

    # Total students
    total_students = Student.query.count()

    # Today's entries
    total_entries = Attendance.query.filter_by(
        scan_date=today,
        scan_type="ENTRY"
    ).count()

    # Today's exits
    total_exits = Attendance.query.filter_by(
        scan_date=today,
        scan_type="EXIT"
    ).count()

    # Students currently inside
    students_inside = max(total_entries - total_exits, 0)

    return render_template(
        "dashboard.html",
        total_students=total_students,
        total_entries=total_entries,
        total_exits=total_exits,
        students_inside=students_inside,
        state=system_state,
        admin_name=session.get("admin_name"),
        admin_role=session.get("admin_role")
    )