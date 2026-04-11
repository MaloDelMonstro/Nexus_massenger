from flask import Flask

from .auth import auth_bp
from .bots import bots_bp
from .chat import chat_bp
from .profile import profile_bp
from .settings import settings_bp
from .messages import messages_bp
from .admin import admin_bp
from .api import api_bp
from .main import main_bp


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(auth_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(messages_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(bots_bp)
    app.register_blueprint(main_bp)
