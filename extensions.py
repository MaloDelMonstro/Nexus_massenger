from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO, emit
from flask_mail import Mail
import os
import shutil
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
socketio = SocketIO()
mail = Mail()


def init_extensions(app: Flask) -> None:
    db.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Пожалуйста, войдите для доступа к этой странице'
    login_manager.login_message_category = 'warning'

    socketio.init_app(
        app,
        cors_allowed_origins="*",
        async_mode='threading',
        ping_timeout=60,
        ping_interval=25
    )
    mail.init_app(app)

    init_template_filters(app)


def init_template_filters(app: Flask) -> None:
    @app.template_filter('format_date')
    def format_date_filter(date, format_str='%d.%m.%Y %H:%M'):
        if not date:
            return 'Неизвестно'
        return date.strftime(format_str)

    @app.template_filter('truncate')
    def truncate_filter(text, length=100):
        if not text:
            return ''
        if len(text) <= length:
            return text
        return text[:length] + '...'

    @app.template_filter('avatar_url')
    def avatar_url_filter(user):
        if user.avatar_url:
            return user.avatar_url
        from utils.helpers import get_avatar_url
        return get_avatar_url(user.username)


def init_login_manager() -> None:
    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        return db.session.get(User, int(user_id))


@socketio.on('roulette_reroll')
def handle_roulette_reroll(data):
    try:
        from plugins.commands.roulette import RoulettePlugin
        import random

        spin_id = data['spin_id']
        options = data['options']
        winner = data['winner']
        r_type = data['type']

        if r_type == 'standard':
            new_opts = [o for o in options if o != winner]
        else:
            new_opts = [o for o in options if o['num'] != winner]

        if len(new_opts) < 2:
            final_html = f"""<div id="wheel-{spin_id}" style="max-width:420px;width:100%;padding:20px;text-align:center;background:linear-gradient(145deg,#1e1b4b,#312e81);border:2px solid #4f46e5;border-radius:12px;color:#FFD700;font-weight:bold;box-sizing:border-box;">
            Финал! Осталось менее 2 вариантов.
            </div>"""
            emit('roulette_updated', {'spin_id': spin_id, 'html': final_html})
            return

        plugin = RoulettePlugin()
        new_winner = random.choice(new_opts)

        if r_type == 'standard':
            title = "РУЛЕТКА"
            accent = "#FFD700"
            new_html = plugin.gen_standard_html(new_opts, new_winner, title, accent, spin_id)
        else:
            cmap = {'g': {'bg': '#22c55e', 'label': 'ЗЕРО'}, 'r': {'bg': '#ef4444', 'label': 'КРАСНОЕ'},
                    'b': {'bg': '#1e293b', 'label': 'ЧЁРНОЕ'}}
            new_html = plugin.gen_casino_html(new_opts, new_winner, cmap, spin_id)

        emit('roulette_updated', {'spin_id': spin_id, 'html': new_html})
    except Exception as e:
        print(f"Roulette reroll error: {e}")


def clear_upload_folder():
    upload_path = Config.UPLOAD_FOLDER
    if os.path.exists(upload_path):
        print(f"Очищаю папку: {upload_path}")
        for filename in os.listdir(upload_path):
            file_path = os.path.join(upload_path, filename)
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        print("Папка очищена.")
    else:
        print(f"Папка не найдена: {upload_path}. Создаю...")
        os.makedirs(upload_path, exist_ok=True)