import cv2

from services.system_state import system_state


class MotionDetector:

    def __init__(self):
        self.previous_frame = None

    def detect_motion(self, frame):

        # Detect motion across the whole camera frame.  A student can present
        # their QR code anywhere in front of the camera; it is not limited to
        # the old fixed detection rectangle.
        zone = frame

        gray = cv2.cvtColor(
            zone,
            cv2.COLOR_BGR2GRAY
        )

        gray = cv2.GaussianBlur(
            gray,
            (21, 21),
            0
        )

        if self.previous_frame is None:
            self.previous_frame = gray
            return False

        frame_delta = cv2.absdiff(
            self.previous_frame,
            gray
        )

        thresh = cv2.threshold(
            frame_delta,
            25,
            255,
            cv2.THRESH_BINARY
        )[1]

        motion_pixels = cv2.countNonZero(thresh)

        self.previous_frame = gray

        return motion_pixels > 4000
