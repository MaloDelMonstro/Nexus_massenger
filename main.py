from flask import Flask

from admin_utils.const import PORT
from config import Config
from extensions import (socketio, clear_upload_folder, _initialize_core_components,
                        _setup_plugins)
from utils.error_handlers import init_error_handlers
from routes import register_blueprints


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    _initialize_core_components(app)
    _setup_plugins(app)
    register_blueprints(app)
    init_error_handlers(app)

    return app


if __name__ == '__main__':
    application = create_app()
    clear_upload_folder()
    socketio.run(
        application,
        host='0.0.0.0',
        port=PORT,
        debug=True,
        allow_unsafe_werkzeug=True
    )
