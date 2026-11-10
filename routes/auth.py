from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.admin import Admin

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/", methods=["GET"])
def home():
    # If already logged in, go to dashboard
    if session.get("admin_id"):
        return redirect(url_for("dashboard.dashboard"))

    return redirect(url_for("auth.login"))


@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        admin = Admin.query.filter_by(username=username).first()

        if admin and admin.check_password(password):

            session["admin_id"] = admin.id
            session["admin_name"] = admin.full_name
            session["admin_role"] = admin.role

            flash("Welcome back!", "success")

            return redirect(url_for("dashboard.dashboard"))

        flash("Invalid username or password.", "danger")

    return render_template("auth/login.html")


@auth_bp.route("/logout")
def logout():

    session.clear()

    flash("You have been logged out.", "info")

    return redirect(url_for("auth.login"))