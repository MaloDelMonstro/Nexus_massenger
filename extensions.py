from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO
from flask_mail import Mail

db = SQLAlchemy()
login_manager = LoginManager()
socketio = SocketIO()
mail = Mail()


def init_extensions(app):
    db.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message = 'Пожалуйста, войдите для доступа к этой странице'
    login_manager.login_message_category = 'warning'

    socketio.init_app(app, cors_allowed_origins="*",
                      async_mode='threading',
                      ping_timeout=60,
                      ping_interval=25)
    mail.init_app(app)