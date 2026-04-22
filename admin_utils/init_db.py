import os
import sys
from datetime import datetime, timezone

from extensions import db
from main import create_app

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def recreate_database():
    app = create_app()

    with app.app_context():
        print("Удаляем старые таблицы...")
        db.drop_all()

        print("Создаём новые таблицы...")
        db.create_all()

        print("Таблицы созданы успешно!")

        create_default_data()

        print("База данных готова к работе!")


def create_default_data():
    from models import User
    from werkzeug.security import generate_password_hash

    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@example.com',
            password=generate_password_hash('admin123'),
            is_verified=True,
            is_admin=True,
            created_at=datetime.now(timezone.utc)
        )
        db.session.add(admin)
        db.session.commit()
        print("Администратор создан: admin / admin123")
    else:
        print("Администратор уже существует.")


if __name__ == '__main__':
    if input('act') == 'recreate':
        recreate_database()
