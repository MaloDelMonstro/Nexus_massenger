from flask import Flask

from admin_utils.const import PORT
from config import Config
from extensions import init_extensions, init_login_manager, socketio, clear_upload_folder
from utils.error_handlers import init_error_handlers
from routes import register_blueprints
from plugins import PluginManager


def create_app() -> Flask:
    main_app = Flask(__name__)
    main_app.config.from_object(Config)

    init_extensions(main_app)

    init_login_manager()

    plugin_manager = PluginManager()
    loaded_plugins = plugin_manager.load_all()
    print(f"\nЗагружено плагинов: {len(loaded_plugins)}")
    main_app.extensions['plugin_manager'] = plugin_manager

    register_blueprints(main_app)

    init_error_handlers(main_app)

    return main_app


if __name__ == '__main__':
    app = create_app()
    clear_upload_folder()
    socketio.run(app, host='0.0.0.0', port=PORT, debug=True, allow_unsafe_werkzeug=True)
