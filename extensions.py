import os
import random
import shutil
from datetime import datetime

from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from flask_socketio import SocketIO, emit
from flask_sqlalchemy import SQLAlchemy

from config import Config
from plugins import PluginManager

db = SQLAlchemy()
login_manager = LoginManager()
socketio = SocketIO()
mail = Mail()


def init_extensions(app: Flask) -> None:
    db.init_app(app)
    login_manager.init_app(app)
    _configure_login_manager()

    socketio.init_app(
        app,
        cors_allowed_origins="*",
        async_mode="threading",
        ping_timeout=60,
        ping_interval=25,
    )

    mail.init_app(app)
    _init_template_filters(app)


def _configure_login_manager() -> None:
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Пожалуйста, войдите для доступа к этой странице"
    login_manager.login_message_category = "warning"


def _init_template_filters(app: Flask) -> None:
    @app.template_filter("format_date")
    def _format_date_filter(date: datetime | None, format_str: str = "%d.%m.%Y %H:%M") -> str:
        return date.strftime(format_str) if date else "Неизвестно"

    @app.template_filter("truncate")
    def _truncate_filter(text: str | None, length: int = 100) -> str:
        if not text:
            return ""
        return text if len(text) <= length else f"{text[:length]}..."

    @app.template_filter("avatar_url")
    def _avatar_url_filter(user) -> str:
        if getattr(user, "avatar_url", None):
            return user.avatar_url
        from utils.helpers import get_avatar_url
        return get_avatar_url(user.username)


def init_login_manager() -> None:
    @login_manager.user_loader
    def _load_user(user_id: str):
        from models import User
        return db.session.get(User, int(user_id))


@socketio.on("roulette_reroll")
def _handle_roulette_reroll(data: dict) -> None:
    from plugins.commands.roulette import RoulettePlugin

    spin_id: str = data["spin_id"]
    options: list = data["options"]
    winner = data["winner"]
    roll_type: str = data["type"]

    new_opts: list = [
        opt for opt in options
        if (roll_type == "standard" and opt != winner) or
           (roll_type != "standard" and opt.get("num") != winner)
    ]

    if len(new_opts) < 2:
        _emit_final_state(spin_id)
        return

    plugin = RoulettePlugin()
    new_winner = random.choice(new_opts)

    if roll_type == "standard":
        new_html: str = plugin.gen_standard_html(
            new_opts, new_winner, "РУЛЕТКА", "#FFD700", spin_id
        )
    else:
        color_map: dict[str, dict[str, str]] = {
            "g": {"bg": "#22c55e", "label": "ЗЕРО"},
            "r": {"bg": "#ef4444", "label": "КРАСНОЕ"},
            "b": {"bg": "#1e293b", "label": "ЧЁРНОЕ"},
        }
        new_html = plugin.gen_casino_html(new_opts, new_winner, color_map, spin_id)

    emit("roulette_updated", {"spin_id": spin_id, "html": new_html})


def _emit_final_state(spin_id: str) -> None:
    final_html: str = (
        f'<div id="wheel-{spin_id}" style="max-width:420px;width:100%;'
        'padding:20px;text-align:center;background:linear-gradient(145deg,#1e1b4b,#312e81);'
        'border:2px solid #4f46e5;border-radius:12px;color:#FFD700;font-weight:bold;'
        'box-sizing:border-box;">Финал! Осталось менее 2 вариантов.</div>'
    )
    emit("roulette_updated", {"spin_id": spin_id, "html": final_html})


def clear_upload_folder() -> None:
    upload_path: str = Config.UPLOAD_FOLDER

    if not os.path.exists(upload_path):
        os.makedirs(upload_path, exist_ok=True)
        return

    for filename in os.listdir(upload_path):
        file_path: str = os.path.join(upload_path, filename)
        if os.path.isfile(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)


def _initialize_core_components(app: Flask) -> None:
    init_extensions(app)
    init_login_manager()


def _setup_plugins(app: Flask) -> None:
    plugin_manager = PluginManager()
    plugin_manager.load_all()
    app.extensions['plugin_manager'] = plugin_manager
