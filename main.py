from flask import Flask, render_template
from config import Config
from extensions import init_extensions, db, socketio, login_manager
from models import User
from routes import register_blueprints
from socket_handlers import register_socket_handlers
from admin_utils.const import PORT

app = Flask(__name__)
app.config.from_object(Config)

init_extensions(app)


@login_manager.user_loader
def load_user(user_id: str) -> User | None:
    return db.session.get(User, int(user_id))


register_blueprints(app)

register_socket_handlers(socketio)


@app.errorhandler(404)
def not_found_error(error: Exception) -> tuple[str, int]:
    return render_template('error.html', error='Страница не найдена', code=404), 404


@app.errorhandler(500)
def internal_error(error: Exception) -> tuple[str, int]:
    db.session.rollback()
    return render_template('error.html', error='Внутренняя ошибка сервера', code=500), 500


@app.errorhandler(403)
def forbidden_error(error: Exception) -> tuple[str, int]:
    return render_template('error.html', error='Доступ запрещён', code=403), 403


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
