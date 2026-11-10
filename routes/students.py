from flask import Blueprint, render_template, request, redirect, url_for, flash
from sqlalchemy import or_
from utils.auth import login_required
import os
from werkzeug.utils import secure_filename

from models import db
from models.student import Student
from services.student_service import generate_student_code
from services.qr_generator import generate_qr

students_bp = Blueprint(
    "students",
    __name__,
    url_prefix="/students"
)




# =====================================================
# Add Student
# =====================================================
@students_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_student():

    if request.method == "POST":

        # Get Form Data
        name = request.form["name"]
        student_class = request.form["student_class"]
        section = request.form["section"]
        roll_number = request.form["roll_number"]
        father_name = request.form.get("father_name", "")
        mother_name = request.form.get("mother_name", "")
        phone = request.form.get("phone", "")
        email = request.form.get("email", "")
        address = request.form.get("address", "")

        # Generate Student Code
        student_code = generate_student_code()

        # Upload Photo
        photo = request.files.get("photo")

        photo_filename = None

        if photo and photo.filename != "":

            extension = photo.filename.rsplit(".", 1)[1].lower()

            photo_filename = f"{student_code}.{extension}"

            upload_folder = os.path.join(
                "static",
                "uploads",
                "students"
            )

            os.makedirs(upload_folder, exist_ok=True)

            photo.save(
                os.path.join(
                    upload_folder,
                    photo_filename
                )
            )

        # Create Student
        student = Student(
            student_code=student_code,
            name=name,
            student_class=student_class,
            section=section,
            roll_number=roll_number,
            father_name=father_name,
            mother_name=mother_name,
            phone=phone,
            email=email,
            address=address,
            photo=photo_filename
        )

        db.session.add(student)
        db.session.commit()

        # Generate QR Code
        qr_filename = generate_qr(student.student_code)

        student.qr_code = qr_filename

        db.session.commit()

        flash(
            "Student added successfully!",
            "success"
        )

        return redirect(
            url_for("students.students")
        )

    return render_template(
        "students/add_student.html"
    )


# =====================================================
# Edit Student
# =====================================================
@students_bp.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_student(id):

    student = Student.query.get_or_404(id)

    if request.method == "POST":

        student.name = request.form["name"]
        student.student_class = request.form["student_class"]
        student.section = request.form["section"]
        student.roll_number = request.form["roll_number"]
        student.father_name = request.form.get("father_name", "")
        student.mother_name = request.form.get("mother_name", "")
        student.phone = request.form.get("phone", "")
        student.email = request.form.get("email", "")
        student.address = request.form.get("address", "")

        db.session.commit()

        flash(
            "Student updated successfully!",
            "success"
        )

        return redirect(
            url_for("students.students")
        )

    return render_template(
        "students/edit_student.html",
        student=student
    )


# =====================================================
# Delete Student
# =====================================================
@students_bp.route("/delete/<int:id>", methods=["POST"])
@login_required
def delete_student(id):

    student = Student.query.get_or_404(id)

    # Delete Photo
    if student.photo:

        photo_path = os.path.join(
            "static",
            "uploads",
            "students",
            student.photo
        )

        if os.path.exists(photo_path):
            os.remove(photo_path)

    # Delete QR Code
    if student.qr_code:

        qr_path = os.path.join(
            "static",
            "qrcodes",
            student.qr_code
        )

        if os.path.exists(qr_path):
            os.remove(qr_path)

    db.session.delete(student)
    db.session.commit()

    flash(
        "Student deleted successfully!",
        "success"
    )

    return redirect(
        url_for("students.students")
    )

# =====================================================
# Student List
# =====================================================
@students_bp.route("/")
@login_required
def students():

    # Get search text from URL
    search = request.args.get("search", "").strip()

    # Start database query
    query = Student.query

    # Apply search if user entered something
    if search:
        query = query.filter(
            or_(
                Student.name.ilike(f"%{search}%"),
                Student.roll_number.ilike(f"%{search}%"),
                Student.student_code.ilike(f"%{search}%"),
                Student.student_class.ilike(f"%{search}%"),
                Student.section.ilike(f"%{search}%")
            )
        )

    # Get filtered students
    students = query.all()

    return render_template(
        "students/students.html",
        students=students,
        search=search
    )
# =====================================================
# View Student
# =====================================================
@students_bp.route("/view/<int:id>")
@login_required
def view_student(id):

    student = Student.query.get_or_404(id)

    return render_template(
        "students/view_student.html",
        student=student
    )