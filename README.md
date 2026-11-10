Smart Attendance System
A Flask-based student attendance and classroom entry-monitoring application. The project combines student management, QR-code identification, camera-based motion detection, attendance logging, a live dashboard, configurable operating hours, and Excel reporting.
Project note: This README describes the code in the supplied repository archive. The application currently uses a local SQLite database and a camera attached to the machine running Flask. It is not a cloud-hosted or multi-camera deployment out of the box.

Contents
- Features
- How the system works
- Technology stack
- Project structure
- Requirements
- Installation
- Configuration
- Running the application
- Using the application
- Attendance logic
- Database models
- Routes and API endpoints
- Reports and Telegram notifications
- Troubleshooting
- Security and deployment notes
- Possible future improvements
Features
Student administration
- Create, view, edit, search, and delete student records.
- Store student code, name, class, section, roll number, contact details, address, and photo.
- Generate sequential student codes in the format ST000001.
- Generate a QR-code image containing the student's unique code.
Attendance and scanning
- Read QR codes from a camera using OpenCV and Pyzbar.
- Record each successful scan as an ENTRY or EXIT.
- Apply a five-second per-student duplicate-scan cooldown.
- Show attendance history and recent activity.
- Provide a JSON scanner endpoint for a submitted student code.
Camera and monitoring
- Capture camera frames in a background real-time engine.
- Detect frame-to-frame movement using grayscale conversion, Gaussian blur, image differencing, thresholding, and a motion-pixel threshold.
- Start a configurable QR scan countdown after motion is detected.
- Trigger a siren state if the scan window expires without a successful scan.
- Stream processed camera frames to authenticated browser pages.
Dashboard, settings, and reports
- Display student totals, today's entry and exit counts, and an estimated number of students inside.
- Configure operating hours, lunch start and duration, QR scan timeout, school information, and camera preferences.
- View attendance for a selected date.
- Generate daily .xlsx attendance reports.
- Optionally send a daily report and an alert message through Telegram when Telegram credentials are configured.
How the system works
1. An administrator signs in to the Flask web interface.
2. The administrator registers a student. The application creates a student code and QR-code image.
3. The camera engine reads frames from the configured camera device (the current implementation opens camera index 1).
4. The motion detector compares consecutive frames. When sufficient movement is detected, the countdown service enables QR scanning.
5. Pyzbar decodes a QR code. Its text is treated as the student code and passed to the attendance service.
6. The attendance service verifies that the student exists and that the same student has not scanned within the previous five seconds.
7. The service alternates the student's scan type between ENTRY and EXIT for that calendar day and saves the record in SQLite.
8. The dashboard and activity endpoints read the stored records. The countdown is reset after a successful attendance record.
9. If the scan countdown expires, the alert service activates the siren state and can send a Telegram message if configured.
Important: Entry/exit is inferred by alternating scans. The application does not independently detect a person's physical direction. A missed scan or an incorrect scan can therefore make the inside count inaccurate until records are corrected.
Technology stack
Area	Technology
Language	Python
Web framework	Flask 3.1.1
ORM and database	Flask-SQLAlchemy, SQLAlchemy, SQLite
Frontend	HTML, CSS, JavaScript, Bootstrap 5
Camera and image processing	OpenCV, NumPy
QR-code generation	qrcode, Pillow
QR-code decoding	Pyzbar
Excel reports	OpenPyXL, Pandas
HTTP / Telegram requests	Requests
Environment configuration	python-dotenv


The exact Python package versions are listed in requirements.txt.
Project structure
smart-attendance-system/
├── app.py                       # Flask app factory, database setup, engine startup
├── config.py                    # Application and camera/report configuration
├── requirements.txt             # Python dependencies
├── .env                         # Local environment variables (do not commit secrets)
├── models/
│   ├── __init__.py              # SQLAlchemy database instance
│   ├── admin.py                 # Administrator model and password hashing
│   ├── student.py               # Student model
│   ├── attendance.py            # Attendance event model
│   └── system_setting.py        # Key/value application settings
├── routes/
│   ├── auth.py                  # Login and logout
│   ├── dashboard.py             # Dashboard
│   ├── students.py              # Student CRUD
│   ├── attendance.py            # Attendance history
│   ├── scanner.py               # Scanner page and scan endpoint
│   ├── camera.py                # Camera MJPEG stream
│   ├── video.py                 # Alternate video stream endpoint
│   ├── reports.py               # Date-based report view
│   ├── settings.py              # Settings page
│   ├── api.py                   # Status and alarm reset API
│   └── activity.py              # Recent activity API
├── services/
│   ├── realtime_engine.py       # Camera loop and scheduled system behaviour
│   ├── motion_service.py        # Motion detection
│   ├── qr_service.py             # QR decoding from camera frames
│   ├── qr_generator.py           # Student QR image generation
│   ├── attendance_service.py    # Attendance validation and recording
│   ├── countdown_service.py     # QR scan countdown
│   ├── alert_service.py         # Siren and Telegram alert
│   ├── report_service.py        # Excel report creation and delivery
│   ├── settings_service.py      # Read/write application settings
│   ├── student_service.py       # Student-code generation
│   └── system_state.py          # Shared runtime state
├── templates/                    # Jinja2 HTML templates
├── static/
│   ├── css/                      # Stylesheets
│   ├── js/                       # Frontend JavaScript
│   ├── qrcodes/                  # Generated student QR images
│   └── uploads/students/         # Student photos
├── database/
│   └── school.db                 # SQLite database (created/used by app)
├── exports/                      # Generated Excel reports
├── reports/                      # Report output directory
├── backups/                      # Reserved backup directory
└── utils/
    └── auth.py                   # Login-required route decorator
Some folders and files may be created at runtime. Do not rely on the sample database, uploaded photos, QR images, or exported reports in the repository as production data.
Requirements
- Python 3.10 or newer is recommended.
- A supported operating system with access to a camera.
- A working webcam or USB camera connected to the machine running the application.
- Native ZBar library support for Pyzbar. Installing the Python package alone may not install the native library on every operating system.
- Windows is the most straightforward target for the current camera and beep implementation. The camera code uses OpenCV's CAP_DSHOW backend, and the audible beep uses winsound.
Installation
1. Get the project
Extract the repository ZIP or clone the Git repository, then open a terminal in the project root (the directory containing app.py).
2. Create a virtual environment
Windows PowerShell:
py -m venv .venv
.venv\Scripts\Activate.ps1
Windows Command Prompt:
py -m venv .venv
.venv\Scripts\activate
macOS / Linux:
python3 -m venv .venv
source .venv/bin/activate
3. Install Python dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt
4. Install the native ZBar dependency
Pyzbar depends on the native ZBar shared library.
- Windows: Install a compatible ZBar runtime and ensure its DLL is available on PATH. If Pyzbar reports that it cannot find zbar, install/configure the native runtime before launching the app.
- Ubuntu / Debian: sudo apt-get install libzbar0
- macOS with Homebrew: brew install zbar
The exact installation method may vary by operating system and Python architecture.
5. Configure environment variables
Create a local .env file in the project root. Do not copy real credentials into a public repository.
SECRET_KEY=replace-with-a-long-random-secret
QR_SCAN_WINDOW_SECONDS=5
ALERT_AFTER_SECONDS=10
DAILY_REPORT_TIME=19:53

# Optional Telegram integration
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
The application loads these values through python-dotenv. Telegram settings can be left blank; Telegram delivery is skipped when either value is missing.
Configuration
Application defaults are defined in config.py; many operational values can also be stored in the system_settings database table through the Settings page.
Setting	Purpose
SECRET_KEY	Flask session signing key; set a unique random value
QR_SCAN_WINDOW_SECONDS	Default time allowed for a QR scan after motion
ALERT_AFTER_SECONDS	Delay before the optional manager Telegram alert
DAILY_REPORT_TIME	Time after which the real-time engine sends the daily report once per date
TELEGRAM_BOT_TOKEN	Optional Telegram bot token
TELEGRAM_CHAT_ID	Optional Telegram destination chat ID
SYSTEM_START_TIME / SYSTEM_STOP_TIME	Default operating-hours window in HH:MM format
LUNCH_START / LUNCH_DURATION	Default lunch start and duration
CAMERA_INDEX	Declared camera setting; note that the current real-time engine currently opens index 1 directly


Operational settings include school name, academic year, operating start/stop times, entry window, lunch schedule, QR timeout, alarm delay, camera source/resolution, and auto-logout preference. Check services/settings_service.py for the database defaults.

Camera index: services/realtime_engine.py currently calls cv2.VideoCapture(1, cv2.CAP_DSHOW). If your camera is not detected, change the index/backend to match your device and operating system. The CAMERA_INDEX value in config.py is not currently used by that call.

Time settings: Use 24-hour HH:MM values. The current operating-hours check expects a same-day start and stop interval; overnight schedules need additional handling before use.
Running the application
From the activated virtual environment and project root:
python app.py
The development server is configured for:
http://127.0.0.1:5000
Open that address in a browser. The application creates the required database tables and, if no administrator named admin exists, creates a default administrator account:
Username: admin
Password: admin123
Change this password immediately. The current code creates this default account automatically and does not provide a public registration flow or a password-change page. Do not expose the application to the internet with the default credentials.

The real-time camera engine is started in a daemon thread when app.py is run directly. Running under a multi-worker production server requires changes: each worker must not start its own competing camera capture loop.
Using the application
1. Sign in with the administrator account.
2. Open Students and add a student with the required details.
3. Confirm that a QR-code image is generated for the new student. The QR content is the student's code, for example ST000001.
4. Print or display that QR code for scanning.
5. Connect and position the camera so QR codes can be presented clearly.
6. Open the dashboard or scanner page and check that the camera feed is available.
7. Trigger motion and present the student's QR code within the configured scan window.
8. Check the attendance page, dashboard, or reports page to verify the saved record.
9. Adjust system and lunch hours in Settings to match the institution's schedule.
Attendance logic
The attendance service (services/attendance_service.py) performs the following checks:
- Looks up a student by student_code.
- Rejects unknown student codes.
- Finds the student's latest attendance event.
- Rejects a new scan if it occurs less than five seconds after the previous scan.
- Counts the student's scans for the current date.
- Saves ENTRY when the number of scans for that date is even; otherwise saves EXIT.
This means the first accepted scan of each date is ENTRY, the second is EXIT, the third is ENTRY, and so on. The five-second cooldown is hard-coded in the service; it is not the same as the configurable QR scan window.

The dashboard's current-inside value is calculated from today's total entries minus today's total exits. It is an estimate, not a live occupancy sensor. It can become inaccurate if a student forgets to scan, scans twice in an unintended sequence, or an event is manually changed.
Database models
Model	Table	Main fields
Student	students	Student code, name, class, section, roll number, parent names, phone, email, address, QR filename, photo filename, active status, creation time
Attendance	attendance	Student foreign key, scan date, scan timestamp, scan type (ENTRY / EXIT)
Admin	admins	Name, username, email, password hash, role, active status, creation time, last login
SystemSetting	system_settings	Unique setting key, value, last updated time


The database is SQLite at database/school.db, as configured in config.py. Back up this file before making schema or data changes.
Routes and API endpoints
All listed pages and JSON endpoints are protected by the session-based login_required decorator, except the home, login, and logout routes.
Method	Path	Purpose
GET	/	Redirect to dashboard if signed in, otherwise login
GET, POST	/login	Administrator login
GET	/logout	Clear the session
GET	/dashboard	Dashboard summary
GET	/students/	Student list
GET, POST	/students/add	Add student
GET, POST	/students/edit/<id>	Edit student
POST	/students/delete/<id>	Delete student
GET	/students/view/<id>	Student details
GET	/attendance/	Attendance history
GET	/scanner/	Scanner page
POST	/scanner/scan	Submit a JSON student code for attendance
GET	/reports/	Attendance report view; accepts ?date=YYYY-MM-DD
GET, POST	/settings/	View and save settings
GET	/api/status	Current system state and today's counts as JSON
POST	/api/reset	Stop/reset countdown and alarm state
GET	/activity/recent	Latest ten attendance events as JSON
GET	/camera/feed	Authenticated MJPEG camera stream
GET	/video_feed	Alternate authenticated MJPEG camera stream
GET	/uploads/<path>	Serve files from the uploads directory


Scanner JSON example
POST /scanner/scan expects a JSON body:
{
  "student_code": "ST000001"
}
The response contains a success flag and a message returned by the attendance service. Note that the route currently returns success: true when the service returns a business-level message such as “Student not found”; clients should inspect the message as well.
Status API example
GET /api/status returns fields including camera status, motion state, scanner state, siren state, break mode, system active state, countdown, last student message, total students, today's entries/exits, and estimated students inside.
Reports and Telegram notifications
The report service creates an Excel workbook with student name, student ID, class/section, action, date, time, and weekday. Files are written to the configured export directory with names such as:
exports/attendance-2026-08-04.xlsx
The real-time engine checks the configured daily report time and attempts to generate the report once per date. If Telegram credentials are set, the workbook is sent as a Telegram document. Otherwise, the report is saved locally.

The alert service can send a Telegram message after the configured alert delay if the QR scan countdown expires. On Windows, it also attempts to use winsound for an audible beep. On systems without winsound, the dashboard siren state may still be available, but the Windows beep is not.
Troubleshooting
Camera feed is blank or camera is offline
- Check that the camera is connected and not being used by another application.
- Verify the camera index. The current engine uses index 1; try 0 if that is the device's index.
- On non-Windows systems, replace cv2.CAP_DSHOW with a supported backend or omit the backend argument.
- Confirm that the Flask process has camera permissions.
ImportError or shared-library error from Pyzbar
- Install the native ZBar library for your operating system.
- Ensure the ZBar library/DLL is discoverable by the Python process.
- Confirm that Python, OpenCV, and ZBar use compatible architectures.
QR codes are not detected
- Ensure the QR image is clear, adequately lit, and large enough in the camera frame.
- Confirm the QR contains the exact student code stored in the database.
- Check that the countdown has enabled the scanner.
- Inspect the terminal output for decoded codes and attendance-service messages.
Attendance is not recorded
- Confirm the student exists and is using the correct QR code.
- Wait at least five seconds after the previous scan for that student.
- Check the terminal for database or decoding errors.
- Remember that a second accepted scan on the same day is recorded as EXIT.
Telegram messages or reports are not delivered
- Verify TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID.
- Ensure the bot has permission to message the destination chat.
- Check network access and terminal error messages.
- Reports are still generated locally when Telegram is not configured or delivery fails.
Security and deployment notes
This repository should be treated as a development project until the following items are addressed:
- Replace the default SECRET_KEY fallback with a strong random secret stored outside source control.
- Change the automatically created admin / admin123 credentials before use.
- Remove real .env values, database files containing personal information, student photographs, QR images, and generated reports from public commits.
- Add CSRF protection to state-changing forms and endpoints. Flask-WTF is installed, but its presence in requirements.txt does not by itself mean every form is protected.
- Validate and restrict uploaded photo extensions and content. Use safe filenames and enforce upload limits.
- Add authorization checks for administrator roles if multiple roles are introduced.
- Use HTTPS, secure session-cookie settings, backups, logging, and a production WSGI server for deployment.
- Do not run multiple camera-engine instances against the same physical camera. The current engine is started from the direct app.py entry point and is not designed for multi-worker deployment.
- Review the exposed upload-serving route and avoid making private student data publicly accessible.
- Apply database migrations and tested backup/restore procedures before maintaining real attendance records.
Possible future improvements
- Provide a secure administrator password-change and account-management workflow.
- Make camera index, backend, and resolution fully configurable from the Settings page.
- Add manual attendance correction with an audit trail.
- Support multiple cameras or multiple entrances.
- Replace alternating scan logic with explicit entry/exit selection or direction-aware validation.
- Add pagination and richer filters for attendance and student records.
- Add automated tests for attendance rules, authentication, APIs, and reporting.
- Add database migrations and a documented backup/restore command.
- Add role-based permissions and stronger form/API validation.
License
No license file was present in the supplied project archive. Add a LICENSE file before distributing or accepting external contributions. Until a license is added, the repository does not grant the standard permissions associated with an open-source lic
