import cv2

from pyzbar.pyzbar import decode

from services.system_state import system_state
from services.countdown_service import countdown_service
from services.attendance_service import mark_attendance


class QRService:

    def scan(self, frame):

        # Scanner disabled
        if not system_state.scanner_enabled:
            return

        qr_codes = decode(frame)

        for qr in qr_codes:

            student_code = qr.data.decode("utf-8")

            print(f"QR Detected : {student_code}")

            # Save attendance
            message = mark_attendance(student_code)

            print(message)

            # Save last scanned student
            system_state.last_student = message

            # Update statistics
            if "ENTRY" in message:
                system_state.total_entries += 1
                system_state.students_inside += 1

            elif "EXIT" in message:
                system_state.total_exits += 1

                if system_state.students_inside > 0:
                    system_state.students_inside -= 1

            # An unknown code or a code still in its cooldown must not clear
            # the active scan window.  A successfully recorded scan does.
            if message.endswith("Recorded"):
                countdown_service.stop()
            else:
                continue

            system_state.scanner_enabled = False
            system_state.siren_on = False

            # Draw QR rectangle
            x, y, w, h = qr.rect

            cv2.rectangle(
                frame,
                (x, y),
                (x + w, y + h),
                (0, 255, 0),
                2
            )

            cv2.putText(
                frame,
                student_code,
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )

            # Scan only one QR per frame
            break


qr_service = QRService()
