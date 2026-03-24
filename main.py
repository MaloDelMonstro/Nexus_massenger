from flask import Flask, render_template

from admin_utils.const import PORT
from config import Config
from extensions import init_extensions, db, socketio
from routes import register_blueprints
from socket_handlers import register_socket_handlers


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    init_extensions(app)

    register_blueprints(app)

    register_socket_handlers(socketio)

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('error.html', error='Страница не найдена', code=404), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('error.html', error='Внутренняя ошибка сервера', code=500), 500

    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('error.html', error='Доступ запрещён', code=403), 403

    return app


if __name__ == '__main__':
    app = create_app()

    with app.app_context():
        db.create_all()

    print("\n" + "=" * 60)
    print("🚀 NEXUS MESSENGER ЗАПУЩЕН")
    print("=" * 60)
    print(f"📍 Локально: http://127.0.0.1:{PORT}")
    print(f"🌐 В сети:   http://0.0.0.0:{PORT}")
    print(f"📧 Почта:    {app.config['MAIL_USERNAME']}")
    print("=" * 60 + "\n")

    socketio.run(
        app,
        debug=True,
        host='0.0.0.0',
        port=PORT,
        allow_unsafe_werkzeug=True,
        use_reloader=False
    )
