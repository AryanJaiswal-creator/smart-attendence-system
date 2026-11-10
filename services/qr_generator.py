import os
import qrcode

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

QR_FOLDER = os.path.join(BASE_DIR, "static", "qrcodes")


def generate_qr(student_code):

    os.makedirs(QR_FOLDER, exist_ok=True)

    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=4
    )

    qr.add_data(student_code)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    filename = f"{student_code}.png"

    filepath = os.path.join(QR_FOLDER, filename)

    img.save(filepath)

    return filename