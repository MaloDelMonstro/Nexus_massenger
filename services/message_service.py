from datetime import datetime, timezone

from sqlalchemy import and_, or_
from sqlalchemy.exc import SQLAlchemyError

from extensions import db
from models import Message, PrivateMessage


def create_general_message(content: str, user_id: int, image_url: str | None = None) -> Message:
    msg = Message(content=content, user_id=user_id, image_url=image_url)
    db.session.add(msg)
    try:
        db.session.commit()
        return msg
    except SQLAlchemyError:
        db.session.rollback()
        raise


def create_private_message(content: str, sender_id: int, recipient_id: int) -> PrivateMessage:
    msg = PrivateMessage(content=content, sender_id=sender_id, recipient_id=recipient_id)
    db.session.add(msg)
    try:
        db.session.commit()
        return msg
    except SQLAlchemyError:
        db.session.rollback()
        raise


def get_recent_messages(limit: int = 50) -> list[Message]:
    query = db.session.query(Message).order_by(Message.timestamp.desc()).limit(limit)
    messages = db.session.scalars(query).all()
    messages.reverse()
    return messages


def get_private_messages(user_id: int, recipient_id: int, limit: int = 100) -> list[PrivateMessage]:
    query = db.session.query(PrivateMessage).filter(
        or_(
            and_(PrivateMessage.sender_id == user_id, PrivateMessage.recipient_id == recipient_id),
            and_(PrivateMessage.sender_id == recipient_id, PrivateMessage.recipient_id == user_id),
        )
    ).order_by(PrivateMessage.timestamp.asc()).limit(limit)

    return db.session.scalars(query).all()


def mark_messages_as_read(user_id: int, sender_id: int) -> int:
    query = db.session.query(PrivateMessage).filter_by(
        recipient_id=user_id, sender_id=sender_id, is_read=False
    )
    messages = db.session.scalars(query).all()

    for msg in messages:
        msg.is_read = True

    try:
        db.session.commit()
        return len(messages)
    except SQLAlchemyError:
        db.session.rollback()
        raise


def edit_message(message_id: int, user_id: int, new_content: str) -> tuple[Message | None, str]:
    message = db.session.get(Message, message_id)
    if not message:
        return None, "Сообщение не найдено"
    if message.user_id != user_id:
        return None, "Нет прав на редактирование"
    if not new_content or not new_content.strip():
        return None, "Сообщение не может быть пустым"

    message.content = new_content.strip()
    message.timestamp = datetime.now(timezone.utc)

    try:
        db.session.commit()
        return message, ""
    except SQLAlchemyError:
        db.session.rollback()
        raise


def delete_message(message_id: int, user_id: int) -> tuple[bool, str]:
    message = db.session.get(Message, message_id)
    if not message:
        return False, "Сообщение не найдено"
    if message.user_id != user_id:
        return False, "Нет прав на удаление"

    db.session.delete(message)
    try:
        db.session.commit()
        return True, ""
    except SQLAlchemyError:
        db.session.rollback()
        raise


def get_unread_count(user_id: int) -> int:
    return db.session.query(PrivateMessage).filter_by(
        recipient_id=user_id, is_read=False
    ).count()