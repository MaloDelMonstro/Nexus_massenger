from flask import render_template
from extensions import db


def init_error_handlers(app) -> None:
    @app.errorhandler(404)
    def not_found_error(error) -> tuple[str, int]:
        return render_template('error.html', error='Страница не найдена', code=404), 404

    @app.errorhandler(500)
    def internal_error(error) -> tuple[str, int]:
        db.session.rollback()
        return render_template('error.html', error='Внутренняя ошибка сервера', code=500), 500

    @app.errorhandler(403)
    def forbidden_error(error) -> tuple[str, int]:
        return render_template('error.html', error='Доступ запрещён', code=403), 403