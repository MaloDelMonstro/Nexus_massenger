from flask import Blueprint, Response, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from extensions import db
from models import User
from services.auth_service import (
    register_user_and_send_verification,
    regenerate_verification_token,
    verify_token,
)
from services.user_service import authenticate_user

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login() -> str | Response:
    if current_user.is_authenticated:
        if not current_user.is_verified:
            flash("Пожалуйста, подтвердите email", "warning")
            return redirect(url_for("auth.verify_pending"))
        return redirect(url_for("chat.chat"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = authenticate_user(email, password)

        if user:
            login_user(user)
            flash("Вход выполнен", "success")
            if user.is_verified:
                return redirect(url_for("chat.chat"))
            flash("Пожалуйста, подтвердите email", "warning")
            return redirect(url_for("auth.verify_pending"))

        flash("Неверный email или пароль", "error")

    return render_template("auth.html", mode="login")


@auth_bp.route("/register", methods=["GET", "POST"])
def register() -> str | Response:
    if current_user.is_authenticated:
        return redirect(url_for("chat.chat"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        region = request.form.get("region", "1")

        user, errors = register_user_and_send_verification(
            email=email,
            username=username,
            password=password,
            region=int(region),
        )

        if errors:
            for error in errors:
                flash(error, "error")
            return redirect(url_for("auth.register"))

        flash("Код подтверждения отправлен на email", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth.html", mode="register")


@auth_bp.route("/verify")
def verify_token_page() -> str | Response:
    token = request.args.get("token")
    if not token:
        flash("Токен не указан", "error")
        return redirect(url_for("auth.login"))

    success, msg, user_id = verify_token(token)
    if not success:
        flash(msg, "error")
        return redirect(url_for("auth.login"))

    user = User.query.get(user_id)
    if not user:
        flash("Пользователь не найден", "error")
        return redirect(url_for("auth.login"))

    user.is_verified = True
    db.session.commit()

    login_user(user)
    flash("Email подтверждён!", "success")
    return redirect(url_for("chat.chat"))


@auth_bp.route("/resend-verification", methods=["POST"])
@login_required
def resend_verification() -> Response | tuple[Response, int]:
    email = current_user.email
    success, message = regenerate_verification_token(email)
    if success:
        flash("Новый код отправлен на email", "success")
        return jsonify({"success": True})
    return jsonify({"success": False, "error": message}), 400


@auth_bp.route("/verify-pending")
@login_required
def verify_pending() -> str:
    if current_user.is_verified:
        return redirect(url_for("chat.chat"))
    return render_template("verify_pending.html", email=current_user.email)


@auth_bp.route("/logout")
def logout() -> Response:
    logout_user()
    return redirect(url_for("auth.login"))
