from flask import Flask
from config import Config
from extensions import init_extensions, init_login_manager, db, socketio
from routes import register_blueprints
from socket_handlers import register_socket_handlers
from admin_utils.const import PORT
from utils.error_handlers import init_error_handlers

app = Flask(__name__)
app.config.from_object(Config)

init_extensions(app)
init_error_handlers(app)
init_login_manager()

register_blueprints(app)

register_socket_handlers(socketio)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    print("NEXUS MESSENGER запущен")
    print(f"Локально: http://127.0.0.1:{PORT}")
    print(f"В сети:   http://0.0.0.0:{PORT}")

    socketio.run(
        app,
        debug=True,
        host='0.0.0.0',
        port=PORT,
        allow_unsafe_werkzeug=True,
        use_reloader=False
    )
