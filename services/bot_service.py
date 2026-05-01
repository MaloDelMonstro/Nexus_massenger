import json
import re
from datetime import datetime, timezone

from extensions import db
from models.bot import Bot
from models.message import Message


class BotService:

    @staticmethod
    def create_bot(
            owner_id: int,
            name: str,
            username: str,
            description: str = "",
            avatar_url: str = "",
            is_public: bool = False,
    ) -> tuple[Bot | None, list[str]]:
        errors = []

        if not name or len(name) < 3:
            errors.append("Имя бота должно быть не менее 3 символов")
        if not username or len(username) < 3:
            errors.append("Username должен быть не менее 3 символов")
        if not re.match(r"^[a-zA-Z0-9_]+$", username):
            errors.append("Username может содержать только буквы, цифры и _")

        if db.session.query(Bot).filter_by(name=name).first():
            errors.append("Бот с таким именем уже существует")
        if db.session.query(Bot).filter_by(username=username).first():
            errors.append("Username уже занят")

        if errors:
            return None, errors

        bot = Bot(
            name=name,
            username=username,
            description=description,
            avatar_url=avatar_url,
            owner_id=owner_id,
            is_public=is_public,
        )
        db.session.add(bot)
        db.session.commit()
        return bot, []

    @staticmethod
    def update_bot(bot_id: int, owner_id: int, **kwargs) -> tuple[Bot | None, list[str]]:
        bot = db.session.get(Bot, bot_id)
        if not bot or bot.owner_id != owner_id:
            return None, ["Бот не найден или нет прав"]

        errors = []
        updatable_fields = {"name", "username", "description", "avatar_url", "is_active", "is_public", "auto_reply"}

        for field, value in kwargs.items():
            if field in updatable_fields:
                setattr(bot, field, value)

        if "reply_keywords" in kwargs:
            try:
                json.loads(str(kwargs["reply_keywords"]))
            except (json.JSONDecodeError, TypeError):
                errors.append("Неверный формат ключевых слов")
            else:
                bot.reply_keywords = kwargs["reply_keywords"]

        if "schedule_config" in kwargs:
            try:
                json.loads(str(kwargs["schedule_config"]))
            except (json.JSONDecodeError, TypeError):
                errors.append("Неверный формат расписания")
            else:
                bot.schedule_config = kwargs["schedule_config"]

        if errors:
            return None, errors

        bot.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        return bot, []

    @staticmethod
    def delete_bot(bot_id: int, owner_id: int) -> tuple[bool, str]:
        bot = db.session.get(Bot, bot_id)
        if not bot or bot.owner_id != owner_id:
            return False, "Бот не найден или нет прав"

        db.session.query(Message).filter_by(bot_id=bot_id).delete()
        db.session.delete(bot)
        db.session.commit()
        return True, ""

    @staticmethod
    def send_message_from_bot(bot_id: int, content: str, chat_id: int = 1) -> tuple[Message | None, str]:
        bot = db.session.get(Bot, bot_id)
        if not bot:
            return None, "Бот не найден"

        can_send, error = bot.can_send_message()
        if not can_send:
            return None, error

        cleaned_content = content.strip()
        if not cleaned_content:
            return None, "Сообщение не может быть пустым"

        message = Message(
            content=cleaned_content,
            user_id=None,
            bot_id=bot.id,
        )
        db.session.add(message)
        bot.messages_sent += 1
        bot.last_active = datetime.now(timezone.utc)
        db.session.commit()
        return message, ""

    @staticmethod
    def get_bot_by_id(bot_id: int, owner_id: int | None = None) -> Bot | None:
        bot = db.session.get(Bot, bot_id)
        if not bot:
            return None
        if owner_id and bot.owner_id != owner_id and not bot.is_public:
            return None
        return bot

    @staticmethod
    def get_user_bots(user_id: int, include_inactive: bool = False) -> list[Bot]:
        query = db.session.query(Bot).filter_by(owner_id=user_id)
        if not include_inactive:
            query = query.filter_by(is_active=True)
        return query.order_by(Bot.created_at.desc()).all()

    @staticmethod
    def get_public_bots(limit: int = 20) -> list[Bot]:
        return (
            db.session.query(Bot)
            .filter_by(is_public=True, is_active=True)
            .order_by(Bot.messages_sent.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def process_auto_reply(bot: Bot, incoming_message: str) -> str | None:
        if not bot.auto_reply or not bot.reply_keywords:
            return None

        try:
            keywords = json.loads(bot.reply_keywords)
            incoming_lower = incoming_message.lower()

            for keyword, response in keywords.items():
                if keyword.lower() in incoming_lower:
                    return response
        except (json.JSONDecodeError, TypeError):
            return None

        return None
