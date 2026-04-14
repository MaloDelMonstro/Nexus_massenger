import os
import sys
from datetime import datetime, timezone

from extensions import db
from main import create_app

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def fix_db():
    app = create_app()

    with app.app_context():
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()

        if 'message' in tables:
            columns = [col['name'] for col in inspector.get_columns('message')]
            if 'image_url' not in columns:
                print("Добавляем столбец image_url в таблицу message...")
                db.session.execute(db.text("ALTER TABLE message ADD COLUMN image_url VARCHAR(500);"))
                db.session.commit()
                print("Столбец image_url добавлен.")
            else:
                print("Столбец image_url уже существует.")
        else:
            print("Tаблица message не найдена — возможно, база пуста.")

        print("База данных проверена/исправлена.")


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
        print("Создаём администратора...")
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
    import argparse

    parser = argparse.ArgumentParser(description='Управление базой данных.')
    parser.add_argument('--fix', action='store_true', help='Исправить базу (добавить недостающие поля)')
    parser.add_argument('--recreate', action='store_true', help='Пересоздать базу с нуля')

    args = parser.parse_args()

    if args.fix:
        print("Запуск проверки/исправления базы данных...")
        fix_db()
    elif args.recreate:
        print("Запуск восстановления базы данных...")
        recreate_database()
    else:
        print("Укажите аргумент: --fix или --recreate")
