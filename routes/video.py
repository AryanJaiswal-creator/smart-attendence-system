from flask import Blueprint, Response
import cv2
from utils.auth import login_required
from services.realtime_engine import realtime_engine

# ==========================================
# Video Blueprint
# ==========================================

video_bp = Blueprint(
    "video",
    __name__
)

# ==========================================
# Generate Live Frames
# ==========================================

def generate_frames():

    while True:

        # Wait until first frame is available
        if realtime_engine.frame is None:
            continue

        # Use processed frame from RealtimeEngine
        frame = realtime_engine.frame.copy()

        # Convert frame to JPEG
        ret, buffer = cv2.imencode(".jpg", frame)

        if not ret:
            continue

        frame_bytes = buffer.tobytes()

        # Send frame to browser
        yield (
            b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n'
            + frame_bytes +
            b'\r\n'
        )


# ==========================================
# Video Feed Route
# ==========================================

@video_bp.route("/video_feed")
@login_required
def video_feed():

    return Response(
        generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )