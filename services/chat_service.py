from models import User, Message, PrivateMessage
from extensions import db
from datetime import datetime, timezone, timedelta


def get_chat_profile_data() -> dict:
    admin = User.query.filter_by(is_admin=True).first()

    return {
        'chat_name': admin.chat_name if admin and admin.chat_name else 'Nexus Chat',
        'chat_description': admin.chat_description if admin and admin.chat_description else 'Общий чат мессенджера',
        'chat_avatar': admin.chat_avatar if admin and admin.chat_avatar else None,
        'total_users': User.query.count(),
        'total_messages': Message.query.count()
    }


def get_top_users(limit: int = 5) -> list:
    from sqlalchemy import func

    top_users = db.session.query(
        User.username,
        User.avatar_url,
        func.count(Message.id).label('message_count')
    ).join(Message).group_by(User.id).order_by(
        func.count(Message.id).desc()
    ).limit(limit).all()

    return top_users


def get_recent_messages(limit: int = 10) -> list[Message]:
    return Message.query.order_by(Message.timestamp.desc()).limit(limit).all()


def get_active_users(minutes: int = 5) -> int:
    five_minutes_ago = datetime.now(timezone.utc) - timedelta(minutes=minutes)
    active_users = User.query.filter(
        User.id.in_(
            db.session.query(Message.user_id).filter(
                Message.timestamp >= five_minutes_ago
            ).distinct()
        )
    ).count()

    return active_users or 1


def get_conversations(current_user_id: int) -> list:
    conversations = db.session.query(
        User,
        db.func.count(PrivateMessage.id).label('unread_count'),
        db.func.max(PrivateMessage.timestamp).label('last_message_time')
    ).outerjoin(
        PrivateMessage,
        db.and_(
            db.or_(
                PrivateMessage.sender_id == current_user_id,
                PrivateMessage.recipient_id == current_user_id
            ),
            PrivateMessage.is_read == False,
            PrivateMessage.recipient_id == current_user_id
        )
    ).filter(
        db.or_(
            PrivateMessage.sender_id == current_user_id,
            PrivateMessage.recipient_id == current_user_id
        )
    ).group_by(User.id).order_by(
        db.func.max(PrivateMessage.timestamp).desc().nullslast()
    ).all()

    if not conversations:
        users = User.query.filter(User.id != current_user_id).order_by(User.created_at.desc()).limit(10).all()
        conversations = [(u, 0, None) for u in users]

    return conversations