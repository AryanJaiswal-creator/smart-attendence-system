import threading
import time

from config import Config
from services.alert_service import alert_service
from services.system_state import system_state


class CountdownService:

    def __init__(self):

        self.thread = None

        # Default value
        self.scan_window_seconds = Config.QR_SCAN_WINDOW_SECONDS

    # ==========================================
    # Update Settings
    # ==========================================

    def set_scan_window(self, seconds):

        try:

            seconds = int(seconds)

            if seconds < 1:
                seconds = 1

            self.scan_window_seconds = seconds

            print(
                f"⚙️ QR Scan Timeout Updated: "
                f"{self.scan_window_seconds} seconds"
            )

        except (TypeError, ValueError):

            self.scan_window_seconds = (
                Config.QR_SCAN_WINDOW_SECONDS
            )

    # ==========================================
    # Start Countdown
    # ==========================================

    def start(self):

        # Never start during lunch
        if system_state.break_mode:
            return

        # Never start when system is inactive
        if not system_state.system_active:
            return

        # Prevent multiple countdowns
        if system_state.processing:
            return

        system_state.processing = True

        self.thread = threading.Thread(
            target=self.run,
            daemon=True
        )

        self.thread.start()

    # ==========================================
    # Countdown Logic
    # ==========================================

    def run(self):

        system_state.countdown_running = True

        seconds = self.scan_window_seconds

        system_state.countdown_seconds = seconds

        system_state.scanner_enabled = True

        print(
            f"⏳ Countdown Started: "
            f"{seconds} seconds"
        )

        while system_state.countdown_seconds > 0:

            # ==================================
            # Scheduled interruption
            # ==================================

            if (
                system_state.break_mode
                or not system_state.system_active
            ):

                print(
                    "⏸️ Countdown stopped "
                    "because system is inactive."
                )

                self.stop()

                return

            print(
                f"Countdown : "
                f"{system_state.countdown_seconds}"
            )

            time.sleep(1)

            system_state.countdown_seconds -= 1

            # QR already processed
            if not system_state.processing:

                print("✅ Countdown Cancelled")

                return

        # ==========================================
        # Timeout
        # ==========================================

        system_state.countdown_running = False

        # Keep scanner enabled so valid QR
        # can still stop the siren.
        system_state.scanner_enabled = True

        # Do not start siren during lunch/system stop
        if (
            system_state.break_mode
            or not system_state.system_active
        ):

            self.stop()

            return

        alert_service.start_siren()

        system_state.siren_on = True

        print("🚨 SIREN STARTED")

    # ==========================================
    # Stop Countdown
    # ==========================================

    def stop(self):

        system_state.processing = False

        system_state.countdown_running = False

        system_state.countdown_seconds = (
            self.scan_window_seconds
        )

        system_state.scanner_enabled = False

        system_state.siren_on = False

        alert_service.stop_siren()

        print("✅ Countdown Reset")


countdown_service = CountdownService()