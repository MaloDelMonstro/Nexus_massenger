from datetime import datetime, timedelta, timezone

from sqlalchemy import func

from extensions import db
from models import Message, PrivateMessage, User


def get_chat_profile_data() -> dict:
    admin = db.session.query(User).filter_by(is_admin=True).first()

    return {
        "chat_name": admin.chat_name if admin and admin.chat_name else "Nexus Chat",
        "chat_description": admin.chat_description if admin and admin.chat_description else "Общий чат мессенджера",
        "chat_avatar": admin.chat_avatar if admin and admin.chat_avatar else None,
        "total_users": db.session.query(User).count(),
        "total_messages": db.session.query(Message).count(),
    }


def get_top_users(limit: int = 5) -> list:
    query = db.session.query(
        User.username.label("username"),
        User.avatar_url.label("avatar_url"),
        func.count(Message.id).label("message_count")
    ).join(
        Message, User.id == Message.user_id
    ).group_by(
        User.id, User.username, User.avatar_url
    ).order_by(
        func.count(Message.id).desc()
    ).limit(limit)

    return query.all()


def get_recent_messages(limit: int = 10) -> list[Message]:
    return db.session.query(Message).order_by(Message.timestamp.desc()).limit(limit).all()


def get_active_users(minutes: int = 5) -> int:
    threshold = datetime.now(timezone.utc) - timedelta(minutes=minutes)
    active_subquery = db.session.query(Message.user_id).filter(
        Message.timestamp >= threshold
    ).distinct().subquery()

    count = db.session.query(User).filter(
        User.id.in_(active_subquery)
    ).count()

    return count if count else 1


def get_conversations(current_user_id: int) -> list:
    query = db.session.query(
        User,
        func.count(PrivateMessage.id).label("unread_count"),
        func.max(PrivateMessage.timestamp).label("last_message_time")
    ).outerjoin(
        PrivateMessage,
        (PrivateMessage.sender_id == current_user_id) |
        ((PrivateMessage.recipient_id == current_user_id) & PrivateMessage.is_read.is_(False))
    ).filter(
        (User.id != current_user_id) &
        (
                (PrivateMessage.sender_id == current_user_id) |
                (PrivateMessage.recipient_id == current_user_id) |
                PrivateMessage.id.is_(None)
        )
    ).group_by(
        User.id
    ).order_by(
        func.max(PrivateMessage.timestamp).desc().nullslast()
    )

    results = query.all()

    if not results:
        users = db.session.query(User).filter(
            User.id != current_user_id
        ).order_by(User.created_at.desc()).limit(10).all()
        return [(u, 0, None) for u in users]

    return results
