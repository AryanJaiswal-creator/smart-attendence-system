from flask import Flask
import os
import threading

from config import Config

from models import db
from models.student import Student

from routes.dashboard import dashboard_bp
from routes.students import students_bp
from routes.attendance import attendance_bp
from routes.scanner import scanner_bp
from routes.api import api_bp
from flask import send_from_directory
from routes.activity import activity_bp
from routes.video import video_bp
from routes.auth import auth_bp
from routes.camera import camera_bp
from routes.reports import reports_bp

from services.realtime_engine import realtime_engine
from routes.settings import settings_bp


# =====================================================
# Initialize Database
# =====================================================

def create_app():

    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)

    # ==========================================
    # Register Blueprints
    # ==========================================

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(students_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(scanner_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(activity_bp)
    app.register_blueprint(video_bp)
    app.register_blueprint(camera_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(auth_bp)

    # ==========================================
    # Create Required Folders
    # ==========================================

    folders = [

        "database",

        "uploads",

        "uploads/students",

        "static/qrcodes",

        "reports",

        "backups",

        "exports"

    ]

    for folder in folders:

        os.makedirs(
            folder,
            exist_ok=True
        )

    # ==========================================
    # Create Database Tables
    # ==========================================

    with app.app_context():
        from models.admin import Admin
        from models.student import Student


        db.create_all()

        

        admin = Admin.query.filter_by(username="admin").first()

        if admin is None:
            admin = Admin(
                full_name="Administrator",
                username="admin",
                email="admin@scems.com",
                role="Super Admin"
            )
            admin.set_password("admin123")

            db.session.add(admin)

            db.session.commit()

            print("✅ Default Admin Created")

    return app


# =====================================================
# Start Realtime Engine
# =====================================================

def start_realtime_engine(app):

    with app.app_context():

        realtime_engine.run()


# =====================================================
# Create Flask App
# =====================================================

app = create_app()
from services.settings_service import get_int_setting

with app.app_context():

    print(
        "QR TIMEOUT:",
        get_int_setting(
            "qr_scan_timeout",
            5
        )
    )

@app.route("/uploads/<path:filename>")
def uploaded_file(filename):

    return send_from_directory(
        "uploads",
        filename
    )
# =====================================================
# Run Application
# =====================================================

if __name__ == "__main__":

    # Start camera only once in debug mode
    if (
        not app.debug
        or os.environ.get("WERKZEUG_RUN_MAIN") == "true"
    ):

        realtime_thread = threading.Thread(

    target=start_realtime_engine,

    args=(app,),

    daemon=True

)

        realtime_thread.start()

        print("✅ Realtime Engine Started")

    app.run(
    host="127.0.0.1",
    port=5000,
    debug=True,
    threaded=True,
    use_reloader=False
)