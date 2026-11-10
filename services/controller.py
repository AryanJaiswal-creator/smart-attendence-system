from services.system_state import system_state
from services.motion_service import MotionDetector
from services.countdown_service import countdown_service


class SystemController:

    def __init__(self):

        self.motion_detector = MotionDetector()

    def on_motion_detected(self):

        if system_state.countdown_running:
            return

        print("Motion Detected")

        countdown_service.start()

    def on_qr_scanned(self):

        print("QR Scanned")

        countdown_service.stop()

    def on_invalid_scan(self):

        print("Invalid QR")

    def on_timeout(self):

        print("Countdown Finished")


controller = SystemController()
