import cv2
import os

from datetime import datetime, timedelta

from config import Config

from services.motion_service import MotionDetector
from services.countdown_service import countdown_service
from services.system_state import system_state
from services.qr_service import qr_service
from services.settings_service import (
    get_setting,
    get_int_setting
)
from services.settings_service import get_setting
from services.report_service import report_service


print("Process ID:", os.getpid())


class RealtimeEngine:

    def __init__(self):

        # ==========================================
        # Open Camera
        # ==========================================

        self.camera = cv2.VideoCapture(
            1,
            cv2.CAP_DSHOW
        )

        self.camera.set(
            cv2.CAP_PROP_FRAME_WIDTH,
            1280
        )

        self.camera.set(
            cv2.CAP_PROP_FRAME_HEIGHT,
            720
        )

        # ==========================================
        # Motion Detector
        # ==========================================

        self.motion_detector = MotionDetector()

        self.frame = None

        self._last_lunch_date = None
        self._last_report_date = None

        # ==========================================
        # Settings Cache
        # ==========================================

        self.entry_start_time = Config.ENTRY_START_TIME
        self.entry_end_time = Config.ENTRY_END_TIME

        self.lunch_start = Config.LUNCH_START
        self.lunch_duration = Config.LUNCH_DURATION

    # =====================================================
    # Load Settings
    # =====================================================

    def _load_settings(self):

        self.entry_start_time = get_setting(
            "entry_start_time",
            Config.ENTRY_START_TIME
        )

        self.entry_end_time = get_setting(
            "entry_end_time",
            Config.ENTRY_END_TIME
        )

        self.lunch_start = get_setting(
            "lunch_start",
            Config.LUNCH_START
        )

        self.lunch_duration = get_int_setting(
            "lunch_duration",
            Config.LUNCH_DURATION
        )

        qr_timeout = get_int_setting(
            "qr_scan_timeout",
            Config.QR_SCAN_WINDOW_SECONDS
        )

        countdown_service.set_scan_window(
            qr_timeout
        )

    # =====================================================
    # Operating Hours
    # =====================================================

    def _within_operating_hours(self, now):

        start_time = get_setting(
        "system_start_time",
        Config.SYSTEM_START_TIME
    )

        stop_time = get_setting(
        "system_stop_time",
        Config.SYSTEM_STOP_TIME
    )

    # If either setting is empty,
    # keep the system active all day.
        if not start_time or not stop_time:
            return True

        try:

            start = datetime.strptime(
            start_time,
            "%H:%M"
        ).time()

            stop = datetime.strptime(
            stop_time,
            "%H:%M"
        ).time()

            current = now.time()

            return start <= current < stop

        except (ValueError, TypeError):

            print("⚠️ Invalid system operating time.")

        return True

    def _update_system_active(self, now):

        was_active = system_state.system_active

        system_state.system_active = self._within_operating_hours(now)

    # =====================================
    # SYSTEM STARTED
    # =====================================

        if (
        system_state.system_active
        and not was_active
    ):

            print("🟢 SYSTEM STARTED")

            system_state.scanner_enabled = False
            system_state.motion_detected = False
            system_state.processing = False

    # =====================================
    # SYSTEM STOPPED
    # =====================================

        elif (
        not system_state.system_active
        and was_active
    ):

            print("🔴 SYSTEM STOPPED")

            countdown_service.stop()

            system_state.scanner_enabled = False
            system_state.motion_detected = False
            system_state.processing = False
            system_state.siren_on = False

    # =====================================================
    # Lunch Mode
    # =====================================================

    def _update_lunch_mode(self, now):

        try:

        # =====================================
        # If system itself is OFF
        # don't activate lunch mode
        # =====================================

            if not system_state.system_active:

                if system_state.break_mode:

                    print("🔴 System stopped - Lunch mode cancelled")

                system_state.break_mode = False

                return

        # =====================================
        # Load Lunch Settings
        # =====================================

            lunch_start_str = get_setting(
            "lunch_start",
            Config.LUNCH_START
        )

            lunch_duration = get_int_setting(
            "lunch_duration",
            Config.LUNCH_DURATION
        )

        # =====================================
        # Validate Duration
        # =====================================

            if lunch_duration < 1:
                lunch_duration = Config.LUNCH_DURATION

        # =====================================
        # Convert Lunch Start
        # =====================================

            lunch_start_time = datetime.strptime(
            lunch_start_str,
            "%H:%M"
        ).time()

        # =====================================
        # Calculate Lunch Start / End
        # =====================================

            lunch_start = datetime.combine(
            now.date(),
            lunch_start_time
        )

            lunch_end = lunch_start + timedelta(
            minutes=lunch_duration
        )

        # =====================================
        # Previous State
        # =====================================

            was_break_mode = system_state.break_mode

        # =====================================
        # Current Lunch State
        # =====================================

            system_state.break_mode = (
            lunch_start <= now < lunch_end
        )

        # =====================================
        # LUNCH STARTED
        # =====================================

            if (
            system_state.break_mode
            and not was_break_mode
        ):

                print("🍱 Lunch Break Started")

            # Stop countdown
                countdown_service.stop()

            # Disable scanner
                system_state.scanner_enabled = False

            # Clear motion
                system_state.motion_detected = False

            # Stop processing
                system_state.processing = False

            # Stop siren
                system_state.siren_on = False

        # =====================================
        # LUNCH FINISHED
        # =====================================

            elif (
            was_break_mode
            and not system_state.break_mode
        ):

                print("✅ Lunch Break Finished")

            # Make sure scanner is disabled
                system_state.scanner_enabled = False

            # Clear old motion
                system_state.motion_detected = False

            # Reset processing
                system_state.processing = False

                print("🟢 System ready after lunch")

        except (ValueError, TypeError):

            print("⚠️ Invalid lunch settings.")

            system_state.break_mode = False

    # =====================================================
    # Scheduled Report
    # =====================================================

    def _send_scheduled_report(self, now):

        if (
            Config.DAILY_REPORT_TIME
            and now.strftime("%H:%M")
            >= Config.DAILY_REPORT_TIME
            and self._last_report_date
            != now.date()
        ):

            report_service.send_daily_report(
                now.date()
            )

            self._last_report_date = now.date()

    # =====================================================
    # Start Engine
    # =====================================================

    def run(self):

        print(
            "======================================"
        )

        print(
            "RealtimeEngine.run() called"
        )

        print(
            "======================================"
        )

        if not self.camera.isOpened():

            print(
                "❌ Camera could not be opened."
            )

            return

        print(
            "✅ Camera opened successfully"
        )

        system_state.camera_online = True

        system_state.motion_detected = False

        system_state.scanner_enabled = False

        system_state.siren_on = False

        system_state.break_mode = False

        # ==========================================
        # FPS
        # ==========================================

        fps = 0

        previous_time = cv2.getTickCount()

        # ==========================================
        # Settings Reload Timer
        # ==========================================

        last_settings_reload = datetime.now()

        # ==========================================
        # Main Loop
        # ==========================================

        while True:

            success, frame = self.camera.read()

            now = datetime.now()
            print(
                "SYSTEM TIME:",
                Config.SYSTEM_START_TIME,
                "→",
                Config.SYSTEM_STOP_TIME,
                "| CURRENT:",
                now.strftime("%H:%M:%S")
            )

            if not success:

                print(
                    "❌ Failed to read frame"
                )

                break

            # ==========================================
            # Reload Settings Every 2 Seconds
            # ==========================================

            if (
                now - last_settings_reload
            ).total_seconds() >= 2:

                self._load_settings()

                last_settings_reload = now

            # ==========================================
            # Operating Hours
            # ==========================================

            self._update_system_active(
                now
            )

            # ==========================================
            # Lunch Mode
            # ==========================================

            self._update_lunch_mode(
                now
            )

            # ==========================================
            # Daily Report
            # ==========================================

            self._send_scheduled_report(
                now
            )

            # ==========================================
            # FPS
            # ==========================================

            current_time_tick = (
                cv2.getTickCount()
            )

            time_elapsed = (
                current_time_tick
                -
                previous_time
            ) / cv2.getTickFrequency()

            previous_time = (
                current_time_tick
            )

            if time_elapsed > 0:

                fps = int(
                    1 / time_elapsed
                )

            H, W = frame.shape[:2]

            # ==========================================
            # Motion Detection
            # ==========================================

            motion = (
                self.motion_detector
                .detect_motion(frame)
            )

            system_state.motion_detected = motion

            # ==========================================
            # Motion → Countdown
            # ==========================================

            if (
                motion
                and system_state.system_active
                and not system_state.break_mode
            ):

                cv2.putText(
                    frame,
                    "MOTION DETECTED",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 0),
                    2
                )

                if not system_state.countdown_running:

                    countdown_service.start()

            # ==========================================
            # QR Scanner
            # ==========================================

            if system_state.scanner_enabled:

                qr_service.scan(
                    frame
                )

            # ==========================================
            # Header
            # ==========================================

            header_h = 80

            cv2.rectangle(
                frame,
                (0, 0),
                (W, header_h),
                (25, 25, 25),
                -1
            )

            cv2.line(
                frame,
                (0, header_h),
                (W, header_h),
                (0, 180, 255),
                2
            )

            cv2.putText(
                frame,
                "SMART CLASSROOM ENTRY MONITORING SYSTEM",
                (20, 45),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2
            )

            current_time = (
                datetime.now()
                .strftime(
                    "%d-%m-%Y  %I:%M:%S %p"
                )
            )

            cv2.putText(
                frame,
                current_time,
                (W - 320, 70),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 255),
                2
            )

            # ==========================================
            # Status Panel
            # ==========================================

            cv2.rectangle(
                frame,
                (20, 100),
                (340, 380),
                (40, 40, 40),
                -1
            )

            cv2.rectangle(
                frame,
                (20, 100),
                (340, 380),
                (0, 180, 255),
                2
            )

            cv2.putText(
                frame,
                "SYSTEM STATUS",
                (40, 135),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.75,
                (255, 255, 255),
                2
            )

            # ==========================================
            # Camera Status
            # ==========================================

            camera_color = (
                (0, 255, 0)
                if system_state.camera_online
                else (0, 0, 255)
            )

            cv2.circle(
                frame,
                (50, 180),
                7,
                camera_color,
                -1
            )

            cv2.putText(
                frame,
                "Camera",
                (70, 186),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2
            )

            # ==========================================
            # Motion Status
            # ==========================================

            motion_color = (
                (0, 255, 0)
                if system_state.motion_detected
                else (0, 0, 255)
            )

            cv2.circle(
                frame,
                (50, 215),
                7,
                motion_color,
                -1
            )

            cv2.putText(
                frame,
                "Motion",
                (70, 221),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2
            )

            # ==========================================
            # System Status
            # ==========================================

            system_color = (
                (0, 255, 0)
                if system_state.system_active
                else (0, 0, 255)
            )

            cv2.circle(
                frame,
                (50, 250),
                7,
                system_color,
                -1
            )

            cv2.putText(
                frame,
                "System",
                (70, 256),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2
            )

            # ==========================================
            # Scanner Status
            # ==========================================

            scanner_color = (
                (0, 255, 0)
                if system_state.scanner_enabled
                else (0, 0, 255)
            )

            cv2.circle(
                frame,
                (50, 285),
                7,
                scanner_color,
                -1
            )

            cv2.putText(
                frame,
                "Scanner",
                (70, 291),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2
            )

            # ==========================================
            # Siren Status
            # ==========================================

            siren_color = (
                (0, 0, 255)
                if system_state.siren_on
                else (0, 255, 0)
            )

            cv2.circle(
                frame,
                (50, 320),
                7,
                siren_color,
                -1
            )

            cv2.putText(
                frame,
                "Siren",
                (70, 326),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2
            )

            # ==========================================
            # Lunch Status
            # ==========================================

            if system_state.break_mode:

                cv2.putText(
                    frame,
                    "🍱 LUNCH BREAK",
                    (40, 360),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 200, 255),
                    2
                )

            # ==========================================
            # Countdown
            # ==========================================

            if system_state.countdown_running:

                cv2.rectangle(
                    frame,
                    (15, 105),
                    (280, 145),
                    (0, 0, 0),
                    -1
                )

                cv2.putText(
                    frame,
                    f"Countdown : "
                    f"{system_state.countdown_seconds}",
                    (20, 135),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 255),
                    2
                )

            # ==========================================
            # Last Student
            # ==========================================

            if system_state.last_student:

                cv2.putText(
                    frame,
                    f"Last Scan : "
                    f"{system_state.last_student}",
                    (20, 410),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 255),
                    2
                )

            # ==========================================
            # FPS
            # ==========================================

            cv2.putText(
                frame,
                f"FPS : {fps}",
                (20, H - 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (0, 255, 255),
                2
            )

            self.frame = frame.copy()

        # ==========================================
        # Cleanup
        # ==========================================

        self.camera.release()

        system_state.camera_online = False

        print(
            "Realtime Engine Stopped"
        )


# ==========================================
# Create Engine Object
# ==========================================

realtime_engine = RealtimeEngine()