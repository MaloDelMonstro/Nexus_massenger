from extensions import db
from models import Message, PrivateMessage
from datetime import datetime, timezone


def create_general_message(content: str, user_id: int) -> Message:
    msg = Message(content=content, user_id=user_id)
    db.session.add(msg)
    db.session.commit()
    return msg


def create_private_message(content: str, sender_id: int, recipient_id: int) -> PrivateMessage:
    msg = PrivateMessage(
        content=content,
        sender_id=sender_id,
        recipient_id=recipient_id
    )
    db.session.add(msg)
    db.session.commit()
    return msg


def get_recent_messages(limit: int = 50) -> list[Message]:
    messages = Message.query.order_by(Message.timestamp.desc()).limit(limit).all()
    messages.reverse()
    return messages


def get_private_messages(user_id: int, recipient_id: int, limit: int = 100) -> list[PrivateMessage]:
    messages = PrivateMessage.query.filter(
        db.or_(
            db.and_(PrivateMessage.sender_id == user_id, PrivateMessage.recipient_id == recipient_id),
            db.and_(PrivateMessage.sender_id == recipient_id, PrivateMessage.recipient_id == user_id)
        )
    ).order_by(PrivateMessage.timestamp.asc()).limit(limit).all()

    return messages


def mark_messages_as_read(user_id: int, sender_id: int) -> int:
    messages = PrivateMessage.query.filter_by(
        recipient_id=user_id,
        sender_id=sender_id,
        is_read=False
    ).all()

    for msg in messages:
        msg.is_read = True

    db.session.commit()
    return len(messages)


def edit_message(message_id: int, user_id: int, new_content: str) -> tuple[Message | None, str]:
    message = Message.query.get(message_id)

    if not message:
        return None, 'Сообщение не найдено'

    if message.user_id != user_id:
        return None, 'Нет прав на редактирование'

    if not new_content or not new_content.strip():
        return None, 'Сообщение не может быть пустым'

    message.content = new_content.strip()
    message.timestamp = datetime.now(timezone.utc)
    db.session.commit()

    return message, ''


def delete_message(message_id: int, user_id: int) -> tuple[bool, str]:
    message = Message.query.get(message_id)

    if not message:
        return False, 'Сообщение не найдено'

    if message.user_id != user_id:
        return False, 'Нет прав на удаление'

    db.session.delete(message)
    db.session.commit()

    return True, ''


def get_unread_count(user_id: int) -> int:
    return PrivateMessage.query.filter_by(
        recipient_id=user_id,
        is_read=False
    ).count()
