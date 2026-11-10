from models.student import Student


def generate_student_code():

    last_student = Student.query.order_by(Student.id.desc()).first()

    if last_student is None:
        return "ST000001"

    last_number = int(last_student.student_code.replace("ST", ""))

    new_number = last_number + 1

    return f"ST{new_number:06d}"