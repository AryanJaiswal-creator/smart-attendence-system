from datetime import date, datetime

from flask import Blueprint, render_template, request

from utils.auth import login_required
from models.attendance import Attendance
from models.student import Student

reports_bp = Blueprint(
    "reports",
    __name__,
    url_prefix="/reports"
)


@reports_bp.route("/")
@login_required
def reports():

    # -----------------------------
    # Get Selected Date
    # -----------------------------

    selected_date = request.args.get("date")

    if selected_date:
        try:
            report_date = datetime.strptime(
                selected_date,
                "%Y-%m-%d"
            ).date()

        except ValueError:
            report_date = None

    else:
        report_date = None

    # -----------------------------
    # If no date selected,
    # use latest attendance date
    # -----------------------------

    if report_date is None:

        latest = (
            Attendance.query
            .order_by(
                Attendance.scan_date.desc(),
                Attendance.scan_time.desc()
            )
            .first()
        )

        if latest:
            report_date = latest.scan_date
        else:
            report_date = date.today()

    # -----------------------------
    # Attendance Records
    # -----------------------------

    records = (
        Attendance.query
        .filter_by(scan_date=report_date)
        .order_by(Attendance.scan_time.asc())
        .all()
    )

    # -----------------------------
    # Dashboard Summary
    # -----------------------------

    total_students = Student.query.count()

    present_students = len(
        {
            r.student_id
            for r in records
        }
    )

    absent_students = max(
        total_students - present_students,
        0
    )

    total_entries = len(
        [
            r for r in records
            if r.scan_type == "ENTRY"
        ]
    )

    total_exits = len(
        [
            r for r in records
            if r.scan_type == "EXIT"
        ]
    )

    return render_template(
        "reports/reports.html",
        report_date=report_date,
        records=records,
        total_students=total_students,
        present_students=present_students,
        absent_students=absent_students,
        total_entries=total_entries,
        total_exits=total_exits
    )