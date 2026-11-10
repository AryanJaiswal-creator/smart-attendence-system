from models.system_setting import SystemSetting
from models import db


DEFAULT_SETTINGS = {
    "school_name": "Smart Classroom Entry Monitoring System",
    "academic_year": "2026-2027",


    # ==========================================
    # System
    # ==========================================

    "system_start_time": "",
    "system_stop_time": "",

    # ==========================================
    # Attendance
    # ==========================================

    "entry_start_time": "08:00",
    "entry_end_time": "09:00",

    # ==========================================
    # Lunch
    # ==========================================

    "lunch_start": "11:00",
    "lunch_duration": "20",

    # ==========================================
    # QR / Alarm
    # ==========================================

    "qr_scan_timeout": "5",
    "alarm_delay": "10",

    # ==========================================
    # Camera
    # ==========================================

    "camera_source": "USB Camera",
    "camera_resolution": "1280x720",

    "auto_logout": "false",

}


def get_setting(key, default=None):

    setting = SystemSetting.query.filter_by(
        key=key
    ).first()

    if setting:

        return setting.value

    if default is not None:

        return default

    return DEFAULT_SETTINGS.get(key)


def get_int_setting(key, default=0):

    value = get_setting(
        key,
        str(default)
    )

    try:

        return int(value)

    except (TypeError, ValueError):

        return default


def save_setting(key, value):

    setting = SystemSetting.query.filter_by(
        key=key
    ).first()

    if setting is None:

        setting = SystemSetting(
            key=key,
            value=str(value)
        )

        db.session.add(setting)

    else:

        setting.value = str(value)

    db.session.commit()


def get_all_settings():

    settings = {}

    for key, default in DEFAULT_SETTINGS.items():

        settings[key] = get_setting(
            key,
            default
        )

    return settings