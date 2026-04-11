import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import create_app
from extensions import db
from sqlalchemy import text, inspect


def fix_user_id_column():
    print("🔧 Исправление колонки user_id в таблице message...")
    app = create_app()

    with app.app_context():
        inspector = inspect(db.engine)

        # Проверяем, существует ли таблица
        if 'message' not in inspector.get_table_names():
            print("⚠️ Таблица 'message' не найдена")
            return

        # Проверяем текущие настройки колонки
        columns = {col['name']: col for col in inspector.get_columns('message')}
        user_id_col = columns.get('user_id')

        if not user_id_col:
            print("❌ Колонка user_id не найдена")
            return

        print(f"📊 Текущие настройки user_id: {user_id_col}")

        if user_id_col['nullable'] == True:
            print("✅ user_id уже допускает NULL, всё в порядке!")
            return

        # SQLite: нужно пересоздать таблицу, так как ALTER COLUMN не поддерживается полноценно
        print("🔄 Пересоздаём таблицу message с правильными настройками...")

        try:
            # 1. Временно отключаем внешние ключи
            db.session.execute(text("PRAGMA foreign_keys=off"))

            # 2. Переименовываем старую таблицу
            db.session.execute(text("ALTER TABLE message RENAME TO message_old"))

            # 3. Создаём новую таблицу с правильной схемой
            db.session.execute(text("""
                CREATE TABLE message (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    created_at DATETIME,
                    timestamp DATETIME,
                    user_id INTEGER,
                    bot_id INTEGER,
                    FOREIGN KEY(user_id) REFERENCES user(id),
                    FOREIGN KEY(bot_id) REFERENCES bots(id)
                )
            """))

            # 4. Копируем данные (исключая id, если он autoincrement)
            db.session.execute(text("""
                INSERT INTO message (id, content, created_at, timestamp, user_id, bot_id)
                SELECT id, content, created_at, timestamp, user_id, bot_id FROM message_old
            """))

            # 5. Удаляем старую таблицу
            db.session.execute(text("DROP TABLE message_old"))

            # 6. Включаем внешние ключи обратно
            db.session.execute(text("PRAGMA foreign_keys=on"))

            db.session.commit()
            print("✅ Таблица message успешно обновлена! user_id теперь допускает NULL")

        except Exception as e:
            print(f"❌ Ошибка: {e}")
            db.session.rollback()
            print("💡 Попробуй вручную удалить файл instance/nexus.db (потеряешь только сообщения)")


if __name__ == "__main__":
    fix_user_id_column()