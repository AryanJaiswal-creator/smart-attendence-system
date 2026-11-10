"""Create and optionally deliver the legacy daily attendance report."""

import os
from datetime import date

from openpyxl import Workbook

from config import Config
from models.attendance import Attendance


class ReportService:
    def create_daily_report(self, report_date=None):
        report_date = report_date or date.today()
        records = (Attendance.query.filter_by(scan_date=report_date)
                   .order_by(Attendance.scan_time).all())

        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Attendance"
        sheet.append(["Sr No", "Student Name", "Student ID", "Class", "Action", "Date", "Time", "Day"])
        for number, record in enumerate(records, start=1):
            student = record.student
            sheet.append([
                number, student.name, student.student_code,
                f"{student.student_class}-{student.section}",
                record.scan_type, report_date.isoformat(),
                record.scan_time.strftime("%H:%M:%S"),
                report_date.strftime("%A"),
            ])

        for column in sheet.columns:
            width = max(len(str(cell.value or "")) for cell in column) + 2
            sheet.column_dimensions[column[0].column_letter].width = width
        for cell in sheet[1]:
            cell.font = cell.font.copy(bold=True)

        os.makedirs(Config.EXPORT_FOLDER, exist_ok=True)
        filename = f"attendance-{report_date.isoformat()}.xlsx"
        path = os.path.join(Config.EXPORT_FOLDER, filename)
        workbook.save(path)
        return path

    def send_daily_report(self, report_date=None):
        path = self.create_daily_report(report_date)
        if not (Config.TELEGRAM_BOT_TOKEN and Config.TELEGRAM_CHAT_ID):
            print(f"Daily report saved: {path}")
            return path
        try:
            import requests
            with open(path, "rb") as report:
                response = requests.post(
                    f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/sendDocument",
                    data={"chat_id": Config.TELEGRAM_CHAT_ID, "caption": "Daily Attendance Report"},
                    files={"document": report},
                    timeout=20,
                )
            response.raise_for_status()
            print("Daily attendance report sent")
        except Exception as exc:
            print(f"Daily report delivery failed: {exc}")
        return path


report_service = ReportService()
