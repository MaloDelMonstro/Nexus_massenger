from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO
from flask_mail import Mail

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
