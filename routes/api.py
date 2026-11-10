from flask import Blueprint, jsonify
from datetime import date

from services.system_state import system_state
from models.student import Student
from models.attendance import Attendance
from services.countdown_service import countdown_service
from utils.auth import login_required

api_bp = Blueprint(
    "api",
    __name__,
    url_prefix="/api"
)


@api_bp.route("/status")
@login_required
def status():

    print("\n==============================")
    print("API STATUS CALLED")
    print("==============================")
    print("Camera      :", system_state.camera_online)
    print("Motion      :", system_state.motion_detected)
    print("Scanner     :", system_state.scanner_enabled)
    print("Siren       :", system_state.siren_on)
    print("Countdown   :", system_state.countdown_seconds)
    print("Last Student:", system_state.last_student)
    print("SystemState ID:", id(system_state))
    print("==============================\n")

    today = date.today()

    total_students = Student.query.count()

    total_entries = Attendance.query.filter_by(
        scan_date=today,
        scan_type="ENTRY"
    ).count()

    total_exits = Attendance.query.filter_by(
        scan_date=today,
        scan_type="EXIT"
    ).count()

    students_inside = max(
        0,
        total_entries - total_exits
    )

    return jsonify({

        "camera": system_state.camera_online,

        "motion": system_state.motion_detected,

        "scanner": system_state.scanner_enabled,

        "siren": system_state.siren_on,

        "break_mode": system_state.break_mode,

        "system_active": system_state.system_active,

        "countdown": system_state.countdown_seconds,

        "last_student": system_state.last_student,

        "total_students": total_students,

        "entries": total_entries,

        "exits": total_exits,

        "inside": students_inside

    })


@api_bp.route("/reset", methods=["POST"])
@login_required
def reset_alarm():
    """Teacher's manual reset, equivalent to pressing R in the legacy app."""
    countdown_service.stop()
    return jsonify({"success": True, "message": "Alarm and scanner reset"})
