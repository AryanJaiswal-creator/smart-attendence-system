"""Siren and optional manager alert for an unscanned motion event."""

import threading
import time

from config import Config
from services.system_state import system_state


class AlertService:
    def __init__(self):
        self._thread = None
        self._notification_sent = False

    def start_siren(self):
        if system_state.siren_on:
            return
        system_state.siren_on = True
        self._notification_sent = False
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        print("Siren started: QR scan timed out")

    def stop_siren(self):
        system_state.siren_on = False
        self._notification_sent = False

    def _run(self):
        started = time.monotonic()
        while system_state.siren_on:
            self._beep()
            if (not self._notification_sent and
                    time.monotonic() - started >= Config.ALERT_AFTER_SECONDS):
                self._send_manager_alert()
                self._notification_sent = True
            time.sleep(0.2)

    @staticmethod
    def _beep():
        try:
            import winsound
            winsound.Beep(2500, 500)
        except (ImportError, RuntimeError):
            # The dashboard still displays the alarm on non-Windows hosts.
            pass

    @staticmethod
    def _send_manager_alert():
        if not (Config.TELEGRAM_BOT_TOKEN and Config.TELEGRAM_CHAT_ID):
            print("Manager alert skipped: Telegram is not configured")
            return
        try:
            import requests
            response = requests.post(
                f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": Config.TELEGRAM_CHAT_ID,
                    "text": "Smart student entry alert: QR code was not scanned within 5 seconds.",
                },
                timeout=5,
            )
            response.raise_for_status()
            print("Manager notified")
        except Exception as exc:
            print(f"Manager alert failed: {exc}")


alert_service = AlertService()
