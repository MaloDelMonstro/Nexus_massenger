from flask import Flask

from admin_utils.const import PORT
from config import Config
from extensions import init_extensions, init_login_manager, socketio
from utils.error_handlers import init_error_handlers
from routes import register_blueprints
from plugins.manager import PluginManager


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    init_extensions(app)

    init_login_manager()

    plugin_manager = PluginManager()
    loaded_plugins = plugin_manager.load_all()
    print(f"\nЗагружено плагинов: {len(loaded_plugins)}")
    app.extensions['plugin_manager'] = plugin_manager

    register_blueprints(app)

    init_error_handlers(app)

    return app


if __name__ == '__main__':
    app = create_app()
    socketio.run(app, host='0.0.0.0', port=PORT, debug=True, allow_unsafe_werkzeug=True)
