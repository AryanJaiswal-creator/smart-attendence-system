from flask import Blueprint, Response
import cv2
from utils.auth import login_required
from services.realtime_engine import realtime_engine

camera_bp = Blueprint(
    "camera",
    __name__,
    url_prefix="/camera"
)


def generate_frames():

    while True:

        if realtime_engine.frame is None:
            print("❌ realtime_engine.frame is None")
            continue

        success, buffer = cv2.imencode(
            ".jpg",
            realtime_engine.frame
        )

        if not success:
            continue

        frame = buffer.tobytes()
        print("✅ Sending frame:", len(frame), "bytes")

        yield (
            b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n'
            + frame +
            b'\r\n'
        )


@camera_bp.route("/feed")
@login_required

def camera_feed():

    return Response(
        generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )