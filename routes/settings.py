from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from utils.auth import login_required

from services.settings_service import (
    get_all_settings,
    save_setting
)


settings_bp = Blueprint(
    "settings",
    __name__,
    url_prefix="/settings"
)


@settings_bp.route("/", methods=["GET", "POST"])
@login_required
def settings():

    # =====================================================
    # SAVE SETTINGS
    # =====================================================

    if request.method == "POST":

        # -------------------------------------------------
        # GENERAL
        # -------------------------------------------------

        save_setting(
            "school_name",
            request.form.get(
                "school_name",
                "Smart Classroom Entry Monitoring System"
            )
        )

        save_setting(
            "academic_year",
            request.form.get(
                "academic_year",
                "2026-2027"
            )
        )

        # -------------------------------------------------
        # SYSTEM
        # -------------------------------------------------

        save_setting(
            "system_start_time",
            request.form.get(
                "system_start_time",
                ""
            )
        )

        save_setting(
            "system_stop_time",
            request.form.get(
                "system_stop_time",
                ""
            )
        )

        # -------------------------------------------------
        # ATTENDANCE
        # -------------------------------------------------

        save_setting(
            "entry_start_time",
            request.form.get(
                "entry_start_time",
                "08:00"
            )
        )

        save_setting(
            "entry_end_time",
            request.form.get(
                "entry_end_time",
                "09:00"
            )
        )

        save_setting(
            "qr_scan_timeout",
            request.form.get(
                "qr_scan_timeout",
                "5"
            )
        )

        # -------------------------------------------------
        # LUNCH
        # -------------------------------------------------

        save_setting(
            "lunch_start",
            request.form.get(
                "lunch_start",
                "11:00"
            )
        )

        save_setting(
            "lunch_duration",
            request.form.get(
                "lunch_duration",
                "20"
            )
        )

        # -------------------------------------------------
        # ALARM
        # -------------------------------------------------

        save_setting(
            "alarm_delay",
            request.form.get(
                "alarm_delay",
                "10"
            )
        )

        # -------------------------------------------------
        # CAMERA
        # -------------------------------------------------

        save_setting(
            "camera_source",
            request.form.get(
                "camera_source",
                "USB Camera"
            )
        )

        save_setting(
            "camera_resolution",
            request.form.get(
                "camera_resolution",
                "1280x720"
            )
        )

        # -------------------------------------------------
        # SECURITY
        # -------------------------------------------------

        auto_logout = (
            "true"
            if request.form.get("auto_logout")
            else "false"
        )

        save_setting(
            "auto_logout",
            auto_logout
        )

        flash(
            "Settings saved successfully!",
            "success"
        )

        return redirect(
            url_for("settings.settings")
        )

    # =====================================================
    # LOAD SETTINGS
    # =====================================================

    settings_data = get_all_settings()

    return render_template(
        "settings/settings.html",
        settings=settings_data
    )