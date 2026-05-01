import os
import sys
from datetime import datetime, timezone

from extensions import db
from main import create_app
from models import User
from werkzeug.security import generate_password_hash

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def recreate_database() -> None:
    app = create_app()

    with app.app_context():
        db.drop_all()
        db.create_all()
        create_default_data()


def create_default_data() -> None:
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@nexus.com',
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
    elif input('act') == 'default':
        create_default_data()
