from datetime import datetime, timezone, timedelta

from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user, logout_user

from extensions import db
from models import Message, User, PrivateMessage

chat_bp = Blueprint('chat', __name__, url_prefix='')


@chat_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('chat.chat'))
    return redirect(url_for('auth.login'))


@chat_bp.route('/chat')
@login_required
def chat():
    if not current_user.is_verified:
        flash('Подтвердите email', 'warning')
        return redirect(url_for('auth.verify_email', email=current_user.email))

    if current_user.is_banned:
        flash(f'Аккаунт заблокирован: {current_user.ban_reason}', 'error')
        logout_user()
        return redirect(url_for('auth.login'))

    messages = Message.query.order_by(Message.timestamp.desc()).limit(50).all()
    messages.reverse()

    conversations = db.session.query(
        User,
        db.func.count(PrivateMessage.id).label('unread_count'),
        db.func.max(PrivateMessage.timestamp).label('last_message_time')
    ).outerjoin(
        PrivateMessage,
        db.and_(
            db.or_(
                PrivateMessage.sender_id == current_user.id,
                PrivateMessage.recipient_id == current_user.id
            ),
            PrivateMessage.is_read == False,
            PrivateMessage.recipient_id == current_user.id
        )
    ).filter(
        db.or_(
            PrivateMessage.sender_id == current_user.id,
            PrivateMessage.recipient_id == current_user.id
        )
    ).group_by(User.id).order_by(
        db.func.max(PrivateMessage.timestamp).desc().nullslast()
    ).all()

    if not conversations:
        users = User.query.filter(User.id != current_user.id).order_by(User.created_at.desc()).limit(10).all()
        conversations = [(u, 0, None) for u in users]

    unread_count = PrivateMessage.query.filter_by(
        recipient_id=current_user.id,
        is_read=False
    ).count()

    admin = User.query.filter_by(is_admin=True).first()
    if admin:
        db.session.expire(admin)

    chat_name = admin.chat_name if admin and admin.chat_name else 'Nexus Chat'
    chat_avatar = admin.chat_avatar if admin and admin.chat_avatar else None

    five_minutes_ago = datetime.now(timezone.utc) - timedelta(minutes=5)
    active_users = User.query.filter(
        User.id.in_(
            db.session.query(Message.user_id).filter(
                Message.timestamp >= five_minutes_ago
            ).distinct()
        )
    ).count()

    return render_template('chat.html',
                           messages=messages,
                           chat_name=chat_name,
                           chat_avatar=chat_avatar,
                           active_users=active_users or 1,
                           unread_count=unread_count,
                           conversations=conversations)


@chat_bp.route('/chat/profile')
@login_required
def chat_profile():
    admin = User.query.filter_by(is_admin=True).first()
    if admin:
        db.session.expire(admin)
        db.session.refresh(admin)

    chat_name = admin.chat_name if admin and admin.chat_name else 'Nexus Chat'
    chat_description = admin.chat_description if admin and admin.chat_description else 'Общий чат мессенджера'
    chat_avatar = admin.chat_avatar if admin and admin.chat_avatar else None

    total_users = User.query.count()
    total_messages = Message.query.count()

    top_users = db.session.query(
        User.username,
        User.avatar_url,
        db.func.count(Message.id).label('message_count')
    ).join(Message).group_by(User.id).order_by(
        db.func.count(Message.id).desc()
    ).limit(5).all()

    recent_messages = Message.query.order_by(Message.timestamp.desc()).limit(10).all()

    return render_template('chat_profile.html',
                           total_users=total_users,
                           total_messages=total_messages,
                           top_users=top_users,
                           recent_messages=recent_messages,
                           chat_name=chat_name,
                           chat_description=chat_description,
                           chat_avatar=chat_avatar)
