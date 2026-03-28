from .auth import auth_bp
from .chat import chat_bp
from .profile import profile_bp
from .settings import settings_bp
from .messages import messages_bp
from .admin import admin_bp
from .api import api_bp

def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(messages_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)