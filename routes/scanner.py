from flask import Blueprint, render_template, request, jsonify
from utils.auth import login_required
from services.attendance_service import mark_attendance

scanner_bp = Blueprint(
    "scanner",
    __name__,
    url_prefix="/scanner"
)

@scanner_bp.route("/")
@login_required

def scanner():

    return render_template(
        "scanner/scanner.html"
    )
# ======================================
# Scan QR Code
# ======================================
@scanner_bp.route("/scan", methods=["POST"])
@login_required

def scan_qr():

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "No data received"
        }), 400

    student_code = data.get("student_code")

    if not student_code:
        return jsonify({
            "success": False,
            "message": "Student code missing"
        }), 400

    result = mark_attendance(student_code)

    return jsonify({
        "success": True,
        "message": result
    })
