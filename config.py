import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    # =====================================================
    # Basic Configuration
    # =====================================================
    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "change-this-to-a-random-secret-key"
        )

    # =====================================================
    # Database
    # =====================================================
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(
        BASE_DIR,
        "database",
        "school.db"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # =====================================================
    # Upload Folders
    # =====================================================
    STUDENT_PHOTO_FOLDER = os.path.join(
        BASE_DIR,
        "uploads",
        "students"
    )

    QR_CODE_FOLDER = os.path.join(
        BASE_DIR,
        "static",
        "qrcodes"
    )

    REPORT_FOLDER = os.path.join(
        BASE_DIR,
        "reports"
    )

    BACKUP_FOLDER = os.path.join(
        BASE_DIR,
        "backups"
    )

    EXPORT_FOLDER = os.path.join(
        BASE_DIR,
        "exports"
    )

    # =====================================================
    # School Information
    # =====================================================
    SCHOOL_NAME = "Smart Classroom Entry Monitoring System"

    # =====================================================
    # Attendance Settings
    # =====================================================
    ENTRY_START_TIME = "17:30"
    ENTRY_END_TIME = "17:31"

    # Camera operating hours.  Set both values to empty strings to keep the
    # camera active all day (useful while testing).
    SYSTEM_START_TIME = "17:43"
    SYSTEM_STOP_TIME = "17:45"

    LUNCH_START = "11:00"
    LUNCH_DURATION = 20  # Minutes

    # Number of seconds a student has to present a QR code after motion is
    # detected.  This mirrors the legacy desktop application's SCAN_TIME.
    QR_SCAN_WINDOW_SECONDS = int(os.getenv("QR_SCAN_WINDOW_SECONDS", "5"))
    ALERT_AFTER_SECONDS = int(os.getenv("ALERT_AFTER_SECONDS", "10"))
    DAILY_REPORT_TIME = os.getenv("DAILY_REPORT_TIME", "19:53")

    # Optional.  Keep credentials out of source control; the alert is simply
    # skipped when these environment variables are not set.
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

    # =====================================================
    # Camera Settings
    # =====================================================
    CAMERA_INDEX = 0

    # =====================================================
    # QR Code Settings
    # =====================================================
    QR_VERSION = 1
    QR_BOX_SIZE = 10
    QR_BORDER = 4

    # =====================================================
    # Pagination
    # =====================================================
    STUDENTS_PER_PAGE = 20

    # =====================================================
    # Allowed Uploads
    # =====================================================
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB

    ALLOWED_EXTENSIONS = {
        "png",
        "jpg",
        "jpeg"
    }
